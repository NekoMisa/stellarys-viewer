"""Exercise real CMake release identity generation with disposable source fixtures."""
from pathlib import Path
import argparse, json, shutil, subprocess, tempfile

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--cmake',default='cmake')
args=parser.parse_args()
repo=Path(__file__).resolve().parents[2]
with tempfile.TemporaryDirectory(prefix='stellarys-identity-') as name:
    root=Path(name)
    cmake=root/'indra/cmake'
    cmake.mkdir(parents=True)
    shutil.copyfile(repo/'indra/cmake/StellarysVersion.cmake',cmake/'StellarysVersion.cmake')
    run=root/'run.cmake'
    run.write_text('include("'+(cmake/'StellarysVersion.cmake').as_posix()+'")\nfile(WRITE "'+(root/'channel.txt').as_posix()+'" "${VIEWER_CHANNEL}")\n')
    channels=[]
    for version,variant,valid in [('0.1.4','',True),('0.1.5','',True),
                                 ('0.1.4','Linux Preview 1',True),('0.1.4','Linux Preview 2',True),
                                 ('0.1.4-beta','',False),('0.1','',False),
                                 ('0.1.4','bad"channel',False),('0.1.4','bad;channel',False)]:
        (root/'stellarys-source.json').write_text(json.dumps({'stellarys_version':version}))
        result=subprocess.run([args.cmake,'-DSTELLARYS_CHANNEL_VARIANT='+variant,'-P',str(run)],capture_output=True,text=True)
        assert (result.returncode == 0) == valid, result.stdout+result.stderr
        if valid:
            channel=(root/'channel.txt').read_text()
            assert channel == 'Stellarys Viewer '+version+(' '+variant if variant else '')
            channels.append(channel)
    assert len(channels)==len(set(channels))
print('PASS: 8 release identity cases, including distinct release/preview sources and invalid input refusal')
