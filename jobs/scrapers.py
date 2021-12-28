import requests
from bs4 import BeautifulSoup
from jobs.models import Company, Job


def debug(message, value, flag):
    if not flag:
        return
    print(f'{message}: {str(value)}')


class Scraper:

    @classmethod
    def run(cls, source, flag=False):
        # Prepare variables
        url = f'{source.url}{source.first_page}'
        debug('First page url', url, flag)

        # Looping through all pages
        while url:
            # Get HTML from url & create BeautifulSoup object
            response = requests.get(url)
            debug('Response status code', response.status_code, flag)
            data = response.text
            soup = BeautifulSoup(data, features='html.parser')

            # Get all posted jobs
            jobs = cls.get_job_posts(soup)
            debug('Number of jobs found', len(jobs), flag)

            for job in jobs:
                # Get job data
                title, job_url, company_name, tech_list, desc = cls.get_job_data(job, flag)

                # Prepare title, job_url, company and tech
                title = title.strip()
                if 'https' not in job_url:
                    job_url = source.url + job_url
                company = Company.objects.filter(name=company_name).first()
                if not company:
                    company = Company.objects.create(name=company_name, url='')
                tech = ','.join(tech_list)
                desc = desc.strip()

                # Store data into db
                existing_job = Job.objects.filter(source=source, title=title, company=company).first()
                if existing_job:
                    existing_job.is_active = True
                    existing_job.save()
                else:
                    job = Job.objects.create(source=source, company=company, title=title, desc=desc, url=job_url,
                                             tech=tech)
                    debug('Created job id', job.id, flag)

            # Get new url
            url = cls.get_next_url(soup, source)
            if url and 'https' not in url:
                url = source.url + url
            debug('Next page url', url, flag)

    @staticmethod
    def get_job_posts(soup):
        raise NotImplementedError("Must override get_job_posts")

    @staticmethod
    def get_job_data(job, flag):
        raise NotImplementedError("Must override get_job_data")

    @staticmethod
    def get_next_url(soup, source):
        raise NotImplementedError("Must override get_job_data")


class StartitScraper(Scraper):

    @staticmethod
    def get_job_posts(soup):
        premium_jobs = soup.find_all('article', {'class': 'oglas-premium'})
        standard_jobs = soup.find_all('article', {'class': 'standard-oglas'})
        mini_jobs = soup.find_all('article', {'class': 'mini-oglas'})
        return premium_jobs + standard_jobs + mini_jobs

    @staticmethod
    def get_job_data(job, flag):
        # Get title, job_url, company_name, tech_list and desc
        main_title = job.find('h3').find('a')
        if main_title is None:
            debug('main_title: ', str(main_title), flag)
        title, job_url = main_title.text.strip(),  main_title.get('href')
        mini_header = job.find('h4').find('a')
        if mini_header is None:
            debug('mini_header: ', str(mini_header), flag)
        company_name = mini_header.text.strip()
        company_name = company_name.replace(' → profil kompanije', '')
        tech_list = []

        # Premium jobs tech list
        hidden_div = job.find('div', {'spans-hidden'})
        hidden_spans = hidden_div.find_all('span')
        for hidden_span in hidden_spans:
            if hidden_span.find('a') is None:
                debug("hidden_span.find('a'): ", str(hidden_span.find('a')), flag)
            tech_list.append(hidden_span.find('a').text.strip())
        hidden_as = hidden_div.find_all('a')
        for hidden_a in hidden_as:
            if hidden_a.find('span') is None:
                debug("hidden_a.find('span'): ", str(hidden_a.find('span')), flag)
            tech_list.append(hidden_a.find('span').text.strip())

        # Standard jobs tech list
        div = job.find('div', {'spans'})
        spans = div.find_all('span')
        for span in spans:
            if span.find('a') is None:
                debug("span.find('a'):", str(span.find('a')), flag)
            tech_list.append(span.find('a').text.strip())

        # Mini jobs tech list
        hidden_mini_div = job.find('div', {'spans-m-hidden'})
        hidden_mini_spans = hidden_mini_div.find_all('span')
        for hidden_mini_span in hidden_mini_spans:
            if hidden_mini_span.find('a') is None:
                debug("hidden_mini_span.find('a'): ", str(hidden_mini_span.find('a')), flag)
            tech_list.append(hidden_mini_span.find('a').text.strip())

        return title, job_url, company_name, list(set(tech_list)), ''

    @staticmethod
    def get_next_url(soup, source):
        return None


class HelloworldScraper(Scraper):

    @staticmethod
    def get_job_posts(soup):
        return soup.find_all('div', {'class': 'job-item'})

    @staticmethod
    def get_job_data(job, flag):
        # Get title, job_url, company_name, tech_list and desc
        main_title = job.find('a', {'class': 'job-link'})
        title, job_url = main_title.text, main_title.get('href')
        company_name = ''
        employer = job.find('strong', {'class': '-employer'})
        if employer:
            company_name = employer.find('a').text if employer.find('a') else employer.text
            company_name = company_name.strip()

        # Get tech
        tech_list = []
        job_tags = job.find('div', {'class': 'jobtags'})
        if job_tags:
            for a in job_tags.find_all('a'):
                tech_list.append(a.find('div').text.strip())

        # Get desc
        desc_link = job.find('a', {'class': 'text-link'})
        desc = desc_link.text if desc_link else ''

        return title, job_url, company_name, tech_list, desc

    @staticmethod
    def get_next_url(soup, source):
        next_page = soup.find('div', {'class': 'pagination'}).find('strong').find_next_sibling()
        return next_page.get('href') if next_page else None


class InfostudScraper(Scraper):

    @staticmethod
    def get_job_posts(soup):
        return soup.select('div[id*="oglas_"]')

    @staticmethod
    def get_job_data(job, flag):
        # Get title, job_url, company_name, tech_list and desc
        main_title = job.find('h2').find('a')
        title, job_url = main_title.text, main_title.get('href')
        company_wrapper = job.find('p', {'class': 'uk-h3'})
        company_name = company_wrapper.find('a').text if company_wrapper.find('a') else company_wrapper.text
        company_name = company_name.strip()
        tech_list = [a.text for a in job.find_all('a', {'class': '__jobtag tag-lyt full'})]
        desc_tag = job.find('p', {'class': 'uk-margin-small-bottom'})
        desc = desc_tag.text if desc_tag else ''
        return title, job_url, company_name, tech_list, desc

    @staticmethod
    def get_next_url(soup, source):
        next_page = soup.find('ul', {'uk-pagination'}).find('li', {'class': 'uk-active'}).find_next_sibling().find('a').get('href')
        return next_page or None


class JoobleScraper(Scraper):

    @staticmethod
    def get_job_posts(soup):
        return soup.find_all('div', {'class': 'vacancy_wrapper'})

    @staticmethod
    def get_job_data(job, flag):
        # Get title, job_url, company_name, tech_list and desc
        main_title = job.find('a', {'class': 'link-position'})
        title = ' '.join([e.text.strip() for e in main_title.find('h2').findChildren()])
        job_url = main_title.get('href')
        company_wrapper = job.find('span', {'class': 'company-name'})
        company_name = company_wrapper.text.strip() if company_wrapper else ''
        desc_tag = job.find('span', {'class': 'description'})
        desc = ' '.join(desc_tag.text.split()) if desc_tag else ''
        return title, job_url, company_name, [], desc

    @staticmethod
    def get_next_url(soup, source):
        next_page = soup.find('div', {'id': 'paging'}).find('a', {'class': 'active'}).find_next_sibling().get('data-href')
        return next_page or None
