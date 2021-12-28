from time import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect as redirect_shortcut

from .models import Search


from .models import Job, Source


def index(request):
    sources = Source.objects.filter(is_active=True)
    jobs_count = Job.objects.all().count()
    searches = ','.join([s.term for s in Search.objects.all().order_by('-count')])
    return render(request, 'index.html', {'sources': sources, 'jobs_count': jobs_count, 'searches': searches})


def results(request):
    # Prepare variables
    start_time = time()
    job_list = Job.objects.all().distinct().order_by('-count')
    search = request.GET.get('q', '')
    is_search_form = int(request.GET.get('sf', '0'))
    searches = ','.join([s.term for s in Search.objects.all().order_by('-count')])
    related_searches = []

    # Get results
    if search:
        search = search.strip().lower()

        # Store search term in db if user is using search form only (do not include pagination etc)
        if is_search_form:
            search_obj = Search.objects.filter(term=search).first()
            if search_obj:
                search_obj.count += 1
                search_obj.save()
            else:
                Search.objects.create(term=search)

        # Get related searches
        related_searches = Search.objects.filter(term__icontains=search).exclude(term=search).order_by('-count')[:6]

        # Filtering
        jobs_dict = {}
        for job in Job.objects.filter(title__icontains=search).order_by('-count'):
            if job.id not in jobs_dict:
                jobs_dict[job.id] = job
        for job in Job.objects.filter(tech__icontains=search).order_by('-count'):
            if job.id not in jobs_dict:
                jobs_dict[job.id] = job
        job_list = list(jobs_dict.values())

    # Pagination
    page = request.GET.get('p', 1)
    paginator = Paginator(job_list, 15)
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    diff_time = round(time() - start_time, 2)
    return render(request, 'results.html', {
        'jobs': jobs, 'search': search, 'searches': searches, 'time': diff_time, 'related_searches': related_searches
    })


def redirect(request, job_id):
    # Get job and increment count field
    job = get_object_or_404(Job, id=job_id)
    job.count += 1
    job.save()

    # Redirect to job url
    return redirect_shortcut(job.url)
