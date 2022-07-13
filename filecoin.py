from infura import Infura

class FileCoin(Infura):
    def __init__(self, project_id, project_secret):
        Infura.__init__(self, project_id, project_secret)

    def get_chain_head(self):
        res = self.api_call("Filecoin.ChainHead")
        return res['result']['Height']

    def get_block_messages(self, block):
        print(f"parsing block {block}")
        res = self.api_call("Filecoin.ChainHead")
        cids = res['result']['Cids']
        res = self.api_call("Filecoin.ChainGetTipSetByHeight", [block+1, cids])
        blockCid = res['result']['Cids'][0]['/']
        res = self.api_call("Filecoin.ChainGetParentMessages", [{'/':blockCid}])
        newMessages = res['result']
        res = self.api_call("Filecoin.ChainGetParentReceipts", [{'/':blockCid}])
        newReceipts = res['result']
        msg = [m | r | {'Block': block} for (m,r) in zip(newMessages, newReceipts)]
        return msg

    def get_miner_sector_count(self, miner):
        res = self.api_call("Filecoin.StateMinerSectorCount", [ miner, [] ] )
        return res['result']

    def get_miner_info(self, miner):
        res = self.api_call("Filecoin.StateMinerInfo", [ miner, [] ] )
        return res['result']
