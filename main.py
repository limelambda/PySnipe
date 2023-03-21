import requests, nbt, io, base64, itertools, time
from pynput import keyboard

def main():
    def on_release(key):
            nonlocal inc
            if key == keyboard.Key.f10:
                kb.press('/')
                kb.release('/')
                time.sleep(0.1)
                try:
                    kb.type(f'viewauction {uuids[inc]}\n')
                except IndexError:
                    inc = 0
                inc += 1
            if key == keyboard.Key.f9:
                # Stop listener
                return False

    def get_profitable():

        items = []
        
        def get_attr_from_nbt(raw):
            data = nbt.nbt.NBTFile(fileobj = io.BytesIO(base64.b64decode(raw)))
            # returns TAG_Compound pretty much a dict with the keys 'id', 'attributes' (another TAG_Compund), timestamp, uuid)
            extra_attr = data['i'][0]['tag']['ExtraAttributes']
            return extra_attr
        
        number_pages = requests.get('https://api.hypixel.net/skyblock/auctions').json()['totalPages']
        for page in range(number_pages): #temp just so shits faster :)
            print(f'processing page {page}')
            web_data = requests.get(f'https://api.hypixel.net/skyblock/auctions?page={page}')
            #add a dict with the auction UUID as the key, price & item ID in a tuple to a list if it's BIN
            items.append((str(get_attr_from_nbt(i['item_bytes'])['id']), i['uuid'], i['starting_bid']) for i in (j for j in web_data.json()['auctions'] if j['bin'] == True))
        
        print('Now processing combined data')
        item_prices_dict = {}
        for item_data in itertools.chain.from_iterable(items):
            try:
                item_prices_dict[item_data[0]][item_data[1]] = item_data[2]
            except KeyError:
                item_prices_dict[item_data[0]] = {item_data[1]:item_data[2]}
        print('Now sorting')
        for dict_item_key, dict_item_val in item_prices_dict.items():
            item_prices_dict[dict_item_key] = dict(sorted(dict_item_val.items(), key = lambda val:val[1]))
        uuids = []
        for dict_item_key in item_prices_dict.keys():
            prices = list(item_prices_dict[dict_item_key].values()) 
            try:
                if prices[1] / prices[0] - 1 > 0.1 and prices[1] - prices[0] >= 1000000:
                    uuids.append(list(item_prices_dict[dict_item_key].keys())[0])
            except IndexError:
                pass
        return uuids
    
    inc = 0
    kb = keyboard.Controller()
    uuids = get_profitable()
    listener = keyboard.Listener(on_release=on_release)
    listener.start()
    while True:
        get_profitable()

if __name__ == '__main__':
    main()
