#!/usr/bin/env python

# **Submitter for DQMIO conversion scripts**  
# 
# This script wraps conversion scripts (`harvest_nanodqmio_to_*.py`) in a job.  
# Run with `python harvest_nanodqmio_submit.py -h` for a list of available options.  

### imports
import sys
import os
import argparse
sys.path.append('../jobsubmission')
import condortools as ct
sys.path.append('src')
import tools

if __name__=='__main__':

  # read arguments
  parser = argparse.ArgumentParser(description='Harvest nanoDQMIO to CSV')
  parser.add_argument('--harvester', required=True,
                        help='Harvester to run, should be a valid python script' 
                             +' similar in structure and command line args to'
                             +' e.g. harvest_nanodqmio_to_csv.py.')
  parser.add_argument('--runmode', choices=['condor','local'], default='condor',
                        help='Choose from "condor" or "local";'
                             +' in case of "condor", will submit job to condor cluster;'
                             +' in case of "local", will run interactively in the terminal.')
  parser.add_argument('--filemode', choices=['das','local'], default='das',
                        help='Choose from "das" or "local";'
                              +' in case of "das", will read all files'
                              +' belonging to the specified dataset from DAS;'
                              +' in case of "local", will read all files'
                              +' in the specified folder on the local filesystem.')
  parser.add_argument('--datasetname', required=True,
                        help='Name of the data set on DAS (or filemode "das"'
                             +' OR name of the folder holding input files (for filemode "local"'
                             +' OR comma-separated list of file names'
                             +' (on DAS or locally according to filemode)).'
                             +' Note: interpreted as list of file names if a comma is present,'
                             +' directory or dataset otherwise!')
  parser.add_argument('--redirector', default='root://cms-xrd-global.cern.ch/',
                        help='Redirector used to access remote files'
                             +' (ignored in filemode "local").')
  parser.add_argument('--mename', required=True,
                        help='Name of the monitoring element to store.')
  parser.add_argument('--outputfile', default='test.csv',
                        help='Path to output file.')
  parser.add_argument('--proxy', default=None,
                        help='Set the location of a valid proxy created with'
                             +' "--voms-proxy-init --voms cms";'
                             +' needed for DAS client;'
                             +' ignored if filemode is "local".')
  parser.add_argument('--cmssw', default=None,
                        help='Set the location of a CMSSW release;'
                             +' needed for remote file reading with xrootd.')
  parser.add_argument('--jobflavour', default='workday',
                        help='Set the job flavour in lxplus'
                             +' (see https://batchdocs.web.cern.ch/local/submit.html)')
  parser.add_argument('--istest', default=False, action='store_true',
                        help='If set to true, only one file will be read for speed')
  args = parser.parse_args()
  harvester = args.harvester
  runmode = args.runmode
  filemode = args.filemode
  datasetname = args.datasetname
  redirector = args.redirector
  mename = args.mename
  outputfile = args.outputfile
  proxy = None if args.proxy is None else os.path.abspath(args.proxy)
  cmssw_version = None if args.cmssw is None else os.path.abspath(args.cmssw)
  jobflavour = args.jobflavour
  istest = args.istest

  # print arguments
  print('Running with following configuration:')
  for arg in vars(args):
    print('  - {}: {}'.format(arg,getattr(args,arg)))

  # export the proxy
  if( filemode=='das' or runmode=='condor' ): tools.export_proxy( proxy )

  # make a list of input files
  inputfiles = tools.format_input_files( datasetname,
                                         filemode=filemode,
                                         redirector=redirector,
                                         istest=istest )

  # format the list of input files
  inputfstr = ','.join(inputfiles)
  if len(inputfiles)==1: inputfstr+=','
 
  # make the command
  cmd = 'python {}'.format(harvester)
  cmd += ' --filemode {}'.format(filemode)
  cmd += ' --datasetname {}'.format(inputfstr)
  cmd += ' --redirector {}'.format(redirector)
  cmd += ' --mename {}'.format(mename)
  cmd += ' --outputfile {}'.format(outputfile)
  cmd += ' --proxy {}'.format(proxy)
  if istest: cmd += ' --istest'

  if runmode=='local':
    os.system(cmd)
  if runmode=='condor':
    ct.submitCommandAsCondorJob('cjob_harvest_nanodqmio_submit', cmd,
            home='auto', cmssw_version=cmssw_version, 
            proxy=proxy, jobflavour=jobflavour)
