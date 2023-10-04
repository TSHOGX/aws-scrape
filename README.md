## Scrape Nike Shoes & Store them to DynamoDB with Lambda

Not necessary to use this in practice (long runing time, low frequency). Better to runing once in local to scrape and store data.

Practice of 
- Scraping data using Selenium and BeautifulSoup
- Create Lambda Layers as Python dependences
- Set up AWS Lambda
- Batch add items to DynamoDB

Key Commands
```
conda create --name py37 python=3.7
pip install -t selenium/python/lib/python3.7/site-packages selenium==3.8.0
pip install -t bs4/python/lib/python3.7/site-packages bs4
zip -r headless-chromium.zip chromedriver headless-chromium
```

Download Links
- [chromedriver_linux64](https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip)
- [headless-chromium](https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-41/stable-headless-chromium-amazonlinux-2017-03.zip)

Reference
- [Creating an API that runs Selenium via AWS Lambda - DEV Community](https://dev.to/awscommunity-asean/creating-an-api-that-runs-selenium-via-aws-lambda-3ck3) 