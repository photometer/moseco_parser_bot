BOT_NAME = "moseco"

SPIDER_MODULES = ["moseco.spiders"]
NEWSPIDER_MODULE = "moseco.spiders"

ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    "moseco.pipelines.MosecoPipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

LOG_LEVEL = 'ERROR'
