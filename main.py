from filecoin import FileCoin
from methods import MinerMethods
from model import Model
import argparse
import base64
import cbor2
import os
import shelve

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    project_id = os.environ['PROJECT_ID']
    project_secret = os.environ['PROJECT_SECRET']

    db = shelve.open("filecoin")

    fc = FileCoin(project_id, project_secret)
    head = fc.get_chain_head()

    parser = argparse.ArgumentParser(description='Filecoin energy consumption.')
    parser.add_argument('--begin', dest='begin', default=head-50, type=int,
                        help='first block number (default: head - 50)')
    parser.add_argument('--end', dest='end', default=head, type=int,
                        help='last block number (default: head)')
    parser.add_argument('--miner', dest='miner', type=str,
                        help='miner address (must start with f0')
    args = parser.parse_args()

    if args.begin > args.end or args.end > head:
        print("Invalid range")
        exit(1)
    if args.miner == None or not args.miner.startswith('f0'):
        print("miner address must start with f0")
        exit(1)

    print(f"end {args.end}")

    model = Model()

    filecoin_epoch_s = 30
    time_h = (args.end - args.begin + 1) * filecoin_epoch_s / 3600

    res = fc.get_miner_info(args.miner)
    sector_size = res['SectorSize']

    stored = fc.get_miner_sector_count(args.miner)['Live'] * sector_size
    terabyte = 1024 * 1024 * 1024 * 1024
    print(f"capacity={stored/terabyte} TB")

    commited = 0
    for b in range(args.begin, args.end):
        if str(b) in db:
            msg = db[str(b)]
        else:
            msg = fc.get_block_messages(b)
            db[str(b)] = msg
        fm = [m for m in msg if m['ExitCode'] == 0  and m['Message']['To'] == args.miner]
        for msg in fm:
            parenc = msg['Message']['Params']
            params = []
            if parenc is not None:
                params = cbor2.decoder.loads(base64.b64decode(parenc))
            method = msg['Message']['Method']
#            if method == MinerMethods.PreCommitSectorBatch:
#                commited += sector_size * len(params[0])
            if method == MinerMethods.PreCommitSector:
                commited += sector_size

    print(f"Filecoin  energy consumption for {args.miner} model={model.VERSION}")
    print(f"begin {args.begin} end {args.end} hours={time_h} ")
    for point in ("min", "estimate", "max"):
        sealing = model.parameters['sealing'][point]
        storage = model.parameters['storage'][point]
        pue = model.parameters['pue'][point]
        power_sealing = pue * (sealing * commited / time_h + stored * storage)
        power_storage = pue * (sealing * commited / time_h + stored * storage)
        power = power_sealing + power_storage
        print (f"{point} sealing={power_sealing} W storage={power_storage} total={power} W")
