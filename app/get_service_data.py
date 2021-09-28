import requests
from bs4 import BeautifulSoup
from requests.api import request
from datetime import datetime
from .models import Data
import decimal

async def get_diario_oficial():
    try:
        r = requests.get('https://www.banxico.org.mx/tipcamb/tipCamMIAction.do')
        soup = BeautifulSoup(r.text, 'lxml')
        renglon_titulo_columnas = soup.find("tr", {"class": "renglonNon"})
        rows = renglon_titulo_columnas.parent.find_all('tr')
        data = []
        for row in rows:
            class_name = row.get('class')
            if class_name:
                if 'renglonNon' == class_name[0] or 'renglonPar' == class_name[0] :
                    cols = row.find_all('td')
                    cols = [ele.text.strip() for ele in cols]
                    data.append([ele for ele in cols if ele])

        last_updated = datetime.strptime(data[0][0] + ' ' +'00:00:00' , '%d/%m/%Y %H:%M:%S')
        value = data[0][3]

        data_obj = Data(last_updated=last_updated, value=value, provider=1)
        await data_obj.save()
    except Exception as e :
        pass

async def get_fixer():
    try:
        API_KEY = '3cfd0060dcef4a9efbfb0c59399b2702'

        url = 'http://data.fixer.io/api/latest?access_key={}'.format(API_KEY)
        data = requests.get(url=url).json()

        rates = data.get('rates')['MXN']
        date = datetime.fromtimestamp(data.get('timestamp'))
        
        last_updated = date
        value = rates

        data_obj = Data(last_updated=last_updated, value=value , provider=2)
        await data_obj.save()
    except:
        pass


async def get_banxico():
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        API_KEY = '3f677af17d70f1a192583027368c3efe6ceb9a98300c40e2cf842e4d6090d89c'
        url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SP74665,SF61745,SF60634,SF43718,SF43773/datos/{}/{}'.format(today,today)
        data = requests.get(url, headers={"Bmx-Token": API_KEY }).json()

        result = None
        for i in data['bmx']['series'] :
            if i['idSerie'] == 'SF43718':
                if 'datos' in i:
                    result = i['datos'][0]
                    break
                else: break
        if result:    
            last_updated = datetime.strptime(result['fecha'] + ' ' +'00:00:00' , '%d/%m/%Y %H:%M:%S')

            value = result['dato']

            data_obj = Data(last_updated=last_updated, value=value , provider=3)
            await data_obj.save()
    except:
        pass


async def get_values():
    await get_diario_oficial()
    await get_fixer()
    await get_banxico()

    diario_oficial = await Data.filter(provider=1).order_by('created_at').limit(1).values("value","last_updated")
    fixer = await Data.filter(provider=2).order_by('created_at').limit(1).values("value","last_updated")
    banxico = await Data.filter(provider=3).order_by('created_at').limit(1).values("value","last_updated")

    diario_oficial = diario_oficial[0] if diario_oficial else None
    fixer = fixer[0] if fixer else None
    banxico = banxico[0] if banxico else None

    if diario_oficial:
        diario_oficial['value'] = decimal.Decimal(diario_oficial['value']) 
    if fixer:
        fixer['value'] = decimal.Decimal(fixer['value']) 
    if banxico:
        banxico['value'] = decimal.Decimal(banxico['value']) 

    response_data = {
        'rates' : {
        }
    }
    if diario_oficial:
        response_data['rates']['provider_1'] = diario_oficial
    if fixer:
        response_data['rates']['provider_2'] = fixer
    if banxico:
        response_data['rates']['provider_3'] = banxico

    return response_data