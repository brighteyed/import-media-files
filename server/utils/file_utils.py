from app import app

def is_image_file(filename):
    return filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg')

def is_video_file(filename):
    return filename.lower().endswith('.mp4') or filename.lower().endswith('.mov')

app.jinja_env.globals.update(is_video_file=is_video_file)
