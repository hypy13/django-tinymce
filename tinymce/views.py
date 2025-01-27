# Copyright (c) 2008 Joost Cassee
# Licensed under the terms of the MIT License (see LICENSE.txt)

import json
import os

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from tinymce.compressor import gzip_compressor


def flatpages_link_list(request):
    """
    Returns a HttpResponse whose content is a Javascript file representing a
    list of links to flatpages.
    """
    from django.contrib.flatpages.models import FlatPage

    link_list = [(page.title, page.url) for page in FlatPage.objects.all()]
    return render_to_link_list(link_list)


def compressor(request):
    """
    Returns a GZip-compressed response.
    """
    return gzip_compressor(request)


def render_to_link_list(link_list):
    """
    Returns a HttpResponse whose content is a Javascript file representing a
    list of links suitable for use wit the TinyMCE external_link_list_url
    configuration option. The link_list parameter must be a list of 2-tuples.
    """
    return render_to_js_vardef("tinyMCELinkList", link_list)


def render_to_image_list(image_list):
    """
    Returns a HttpResponse whose content is a Javascript file representing a
    list of images suitable for use wit the TinyMCE external_image_list_url
    configuration option. The image_list parameter must be a list of 2-tuples.
    """
    return render_to_js_vardef("tinyMCEImageList", image_list)


def render_to_js_vardef(var_name, var_value):
    output = f"var {var_name} = {json.dumps(var_value)};"
    return HttpResponse(output, content_type="application/x-javascript")


def filebrowser(request):
    try:
        fb_url = request.build_absolute_uri(reverse("fb_browse"))
    except Exception:
        fb_url = request.build_absolute_uri(reverse("filebrowser:fb_browse"))

    return render(
        request,
        "tinymce/filebrowser.js",
        {"fb_url": fb_url},
        content_type="application/javascript",
    )


@csrf_exempt
def tinymce_upload(request):
    if request.method == 'POST' and 'file' in request.FILES:
        uploaded_file = request.FILES['file']  # Get the uploaded file
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')  # Define the directory path

        # Ensure the directory exists
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)  # Create the directory and any intermediate directories

        file_path = os.path.join(upload_dir, uploaded_file.name)  # Define the file path

        # Save the file manually
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        file_url = f"{settings.MEDIA_URL}uploads/{uploaded_file.name}"

    return JsonResponse({"location": request.build_absolute_uri(file_url)})
