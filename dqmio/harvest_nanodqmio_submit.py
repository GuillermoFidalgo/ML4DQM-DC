### imports
import sys
import os
sys.path.append('../jobsubmission')
import condortools as ct

if __name__=='__main__':

  # definitions
  datasetname = '/MinimumBias/Commissioning2021-900GeVmkFit-v2/DQMIO'
  # (name of the data set on DAS)
  redirector = 'root://cms-xrd-global.cern.ch/'
  # (redirector used to access remote files)
  mename = 'PixelPhase1/Tracks/PXBarrel/chargeInner_PXLayer_1'
  # (name of the monitoring element to store)
  outputfile = 'test.csv'
  # (path to output file)
  exe = 'python harvest_nanodqmio_to_csv.py'
  # (executable to run)
  istest = False 
  # (if set to true, only one file will be read for speed)
  runmode = 'condor'
  # (choose from 'condor' or 'local')
  proxy = os.path.abspath('x509up_u23078')
  # (set the location of a valid proxy)

  # make and execute the DAS client command
  print('running DAS client to find files in dataset {}...'.format(datasetname))
  dascmd = "dasgoclient -query 'file dataset={}' --limit 0".format(datasetname)
  dasstdout = os.popen(dascmd).read()
  dasfiles = [el.strip(' \t') for el in dasstdout.strip('\n').split('\n')]
  if istest: 
    #dasfiles = [dasfiles[0]] 
    dasfiles = [f for f in dasfiles if '7C3F0' in f]
  print('DAS client ready; found following files ({}):'.format(len(dasfiles)))
  for f in dasfiles: print('  - {}'.format(f))
  redirector = redirector.rstrip('/')+'/'
  dasfiles = [redirector+f for f in dasfiles]
  if len(dasfiles)==0:
    raise Exception('ERROR: no files found by the DAS client'
		    +' for the queried dataset {}'.format(datasetname))

  # make the command
  cmd = exe
  cmd += ' '+','.join(dasfiles)
  cmd += ' {}'.format(mename)
  cmd += ' {}'.format(outputfile)

  if runmode=='local':
    os.system(cmd)
  if runmode=='condor':
    ct.submitCommandAsCondorJob('cjob_harvest_nanodqmio_submit', cmd, proxy=proxy)
