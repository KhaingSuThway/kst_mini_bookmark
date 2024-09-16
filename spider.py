import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from pymongo import MongoClient

class RecipeSpider(scrapy.Spider):
    name = "myanmar_recipe"
    start_urls = ['https://www.restaurantguide.com.mm/easy-recipes']
    
    def __init__(self, *args, **kwargs):
        super(RecipeSpider, self).__init__(*args, **kwargs)
        # Connect to MongoDB
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['recipe_database']
        self.collection = self.db['recipes']
        self.recipe_links = set()  # Use a set to avoid duplicates

    def parse(self, response):
        # Extract links to individual recipe pages
        new_links = set(response.css('.media-body a::attr(href)').getall())
        self.recipe_links.update(new_links)
        
        self.logger.info(f'Collected {len(new_links)} new recipe links. Total: {len(self.recipe_links)}')
        
        # Follow pagination
        next_page = response.css('.pagination a:contains("Next")::attr(href)').get()
        if next_page:
            self.logger.info(f'Following next page: {next_page}')
            yield response.follow(next_page, self.parse)
        else:
            self.logger.info('No more pages. Starting to scrape individual recipes.')
            # When we've processed all pages, start scraping individual recipes
            for link in self.recipe_links:
                yield response.follow(link, self.parse_recipe)

    def parse_recipe(self, response):
        recipe_name = response.css('.h-4::text').get()
        ingredients = response.css('p:nth-child(n+7):nth-child(-n+19)::text').getall()
        instructions = response.css('p:nth-child(n+20):nth-child(-n+36)::text').getall()
        
        recipe = {
            'name': recipe_name.strip() if recipe_name else None,
            'ingredients': [ingredient.strip() for ingredient in ingredients if ingredient.strip()],
            'instructions': [instruction.strip() for instruction in instructions if instruction.strip()],
            'url': response.url
        }
        
        # Insert the recipe into MongoDB
        self.collection.insert_one(recipe)
        self.logger.info(f'Scraped recipe: {recipe["name"]}')

    def closed(self, reason):
        # Close the MongoDB connection when the spider is done
        self.client.close()

def run_spider():
    configure_logging()
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    d = runner.crawl(RecipeSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run(installSignalHandlers=0)

if __name__ == '__main__':
    run_spider()