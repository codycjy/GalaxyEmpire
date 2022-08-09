import scrapy
from scrapy.cmdline import execute


execute(['scrapy', 'crawl', 'scan','-aserver=server',
         '-aserver_url=https://example.com', '-ausername=username', '-apassword=password'])
