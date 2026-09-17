"""Download the public source and fail closed if its content has changed."""
from pathlib import Path
import hashlib
from urllib.request import urlopen

ROOT=Path(__file__).resolve().parents[1]
URL='http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv'
EXPECTED='0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece'
target=ROOT/'data/raw/hillstrom.csv'
if target.exists():
    content=target.read_bytes()
else:
    with urlopen(URL,timeout=60) as response: content=response.read()
if hashlib.sha256(content).hexdigest()!=EXPECTED:
    raise RuntimeError('Source checksum differs. Review the new source before proceeding; no file was overwritten.')
target.parent.mkdir(parents=True,exist_ok=True)
target.write_bytes(content)
print(f'Source verified: {len(content):,} bytes; SHA-256 matches the reviewed extract.')
