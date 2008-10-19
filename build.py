import os, shutil, commands
from django.template.loader import render_to_string
from django.conf import settings
from PIL import Image

os.environ['DJANGO_SETTINGS_MODULE'] = u"settings"

def main():
    # retrieving default context dictionary from settings
    context = settings.CONTEXT
    deploy_dir = settings.DEPLOY_DIR
    
    print u"Removing existing deploy dir, if any..."
    shutil.rmtree(deploy_dir,ignore_errors=True)
    
    print u"Creating deploy/ dir..."
    os.mkdir(deploy_dir)

    print u"Copying contents of static/ into deploy/static..."
    deploy_static_dir = os.path.join(deploy_dir,'static')
    os.mkdir(deploy_static_dir)
    static_dir = settings.STATIC_DIR
    compress = settings.YUI_COMPRESSOR

    for filename in os.listdir(static_dir):
        before_ext, ext = os.path.splitext(filename)
        if filename.startswith(".") or filename.endswith("~"):
            print u"Ignored '%s'" % filename
        elif compress and ext in (".js",".css"):
            print u"Compressing and copying '%s' to deploy/static/" % filename
            in_path = os.path.join(static_dir, filename)
            out_path = os.path.join(deploy_static_dir, filename)
            print in_path
            print out_path
            commands.getoutput(u"java -jar %s %s > %s" % (compress, in_path, out_path))
        else:
            print u"Copying '%s' to deploy/static/" % filename
            
    print u"Copying and creating thumbnails for files in images/..."
    deploy_thumb_path = os.path.join(deploy_static_dir,'thumbnail')
    deploy_image_path = os.path.join(deploy_static_dir,'image')
    os.mkdir(deploy_thumb_path)
    os.mkdir(deploy_image_path)

    images = []
    images_dict = {}
    images_dir = settings.IMAGES_DIR
    thumb_format = settings.STATIC_THUMBNAIL_FORMAT
    image_format = settings.STATIC_IMAGE_FORMAT
    thumbnail_dimensions = settings.THUMBNAIL_SIZE

    for filename in os.listdir(images_dir):
        # only process if ends with image file extension
        before_ext,ext = os.path.splitext(filename)
        if ext not in (".png",".jpg",".jpeg"):
            continue

        print u"Copying and thumbnailing %s..." % filename
        filepath = os.path.join(images_dir,filename)
        im = Image.open(filepath)
        im.save(os.path.join(deploy_image_path, filename),ext[1:].upper())
        im.thumbnail(thumbnail_dimensions, Image.ANTIALIAS)
        im.save(os.path.join(deploy_thumb_path, filename), ext[1:].upper())

        # create dict with image data 
        image_dict = {}
        image_dict['filename'] = filename
        image_dict['thumbnail'] = thumb_format % filename
        image_dict['image'] = image_format % filename

        images.append(image_dict)
        # before_ext is 'hello' in 'hello.png'
        images_dict[before_ext] = image_dict

    context['images'] = images
    context['images_dict'] = images_dict

    print u"Rendering pages..."
    pages = settings.PAGES_TO_RENDER
    for page in pages:
        print u"Rendering %s..." % page
        rendered = render_to_string(page,context)
        page_path = os.path.join(deploy_dir,page)
        fout = open(page_path,'w')
        fout.write(rendered)
        fout.close()

    # completed build script
    print u"Done running build.py."

if __name__ == "__main__":
    main()
