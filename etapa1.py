import requests 
import pandas as pd


headers = {
  'Content-Type': 'application/json',
  'token_exact': 'e4b1da77-06aa-4777-a594-cc5bb6e549c4'
}

response = requests.get('https://api.exactspotter.com/v3/QualificationHistories', headers=headers)



df = pd.DataFrame(response)




print(df)


