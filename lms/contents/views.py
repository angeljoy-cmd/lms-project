from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Content, ContentFile, ContentLink, Subject, Topic
from django.contrib import messages
from .forms import ContentForm
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.urls import reverse
import os


User = get_user_model()

@login_required
def upload_content(request):
    sidebar_subjects = get_user_subjects(request.user) 
    # only teachers allowed
    if not request.user.is_teacher:
        messages.error(request, "Only teachers can upload content.")
        return redirect('contents:select_subj')

    # pull subjects & topics for the drop-downs
    subjects = Subject.objects.filter(teacher=request.user)
    topics = Topic.objects.none()
    subject_id = request.GET.get('subject') or request.POST.get('subject')
    subject_obj = None

    if subject_id:
        subject_obj = get_object_or_404(Subject, id=subject_id, teacher=request.user)
        topics = Topic.objects.filter(subject=subject_obj, teacher=request.user)


    if request.method == 'POST':
        # 1) read fields
        title          = request.POST['title']
        description    = request.POST['description']
        new_topic_name = request.POST.get('new_topic', '').strip()
        topic_id       = request.POST.get('topic')
        files          = request.FILES.getlist('files')
        links          = [l.strip() for l in request.POST.getlist('links') if l.strip()]
        student_ids    = request.POST.getlist('students')
        students       = User.objects.filter(id__in=student_ids)

        # 2) create or fetch the Topic
        if new_topic_name:
            topic = Topic.objects.create(
                topic_name=new_topic_name,
                subject=subject_obj,
                teacher=request.user
            )
        else:
            topic = get_object_or_404(Topic, id=topic_id, subject=subject_obj, teacher=request.user)



        # If no topic is selected or created, allow None
        if new_topic_name:
            topic = Topic.objects.create(
                topic_name=new_topic_name,
                subject=subject_obj,
                teacher=request.user
            )
        elif topic_id:
            topic = get_object_or_404(Topic, id=topic_id, subject=subject_obj, teacher=request.user)
        else:
            topic = None

        content = Content.objects.create(
            teacher=request.user,
            title=title,
            description=description,
            subject=subject_obj,
            topic=topic  # May be None
        )

        content.assigned_to.set(students)

        # 4) save each uploaded file
        for f in files:
            ContentFile.objects.create(
                content=content,
                file=f,
                mime_type=f.content_type.split('/')[0]
            )

        # 5) save each link
        for url in links:
            ContentLink.objects.create(
                content=content,
                link=url
            )

        messages.success(request, "Content uploaded successfully!")
        url = reverse('contents:content_list')
        return redirect(f"{url}?subject={subject_obj.id}")

    students = subject_obj.students.all() if subject_obj else User.objects.none()

    return render(request, 'contents/upload_content.html', {
    'subjects':   subjects,
    'topics':     topics,
    'subject_id': subject_id,
    'students':   subject_obj.students.all() if subject_obj else [],
    'sidebar_subjects': sidebar_subjects,
})



User = get_user_model()

def get_user_subjects(user):
    if user.is_authenticated:
        if hasattr(user, 'is_student') and user.is_student:
            return user.subjects_enrolled.all()
        elif hasattr(user, 'is_teacher') and user.is_teacher:
            return Subject.objects.filter(teacher=user)
    return Subject.objects.none()



def get_students_by_subject(request, subject_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        # Replace with your actual relationship to students
        students = subject.students.all()  # OR subject.enrolled_students.all()
        student_data = [
            {
                'id': s.id,
                'username': s.username,
                'full_name': f"{s.first_name} {s.last_name}"
            }
            for s in students
        ]
        return JsonResponse({'students': student_data})
    except Subject.DoesNotExist:
        return JsonResponse({'students': []})


@login_required
def select_subj(request):
    user = request.user
    subjects = get_user_subjects(user)

    return render(request, 'contents/select_subj.html', {
        'subjects': subjects,
        'sidebar_subjects': subjects,  # Pass it here for the sidebar
    })


@login_required
def content_list(request):
    subject_id = request.GET.get('subject')
    topic_id = request.GET.get('topic')

    contents = Content.objects.none()
    topics = []
    subject = None
    sidebar_subjects = get_user_subjects(request.user)

    if subject_id and subject_id.isdigit():
        subject = Subject.objects.filter(id=subject_id).first()
        if subject:
            topics = Topic.objects.filter(subject=subject)

            if request.user.is_teacher:
                contents = Content.objects.filter(subject=subject, teacher=request.user)
            elif request.user.is_student:
                contents = Content.objects.filter(subject=subject, assigned_to=request.user)

            if topic_id and topic_id.isdigit():
                contents = contents.filter(topic__id=topic_id)

    return render(request, 'contents/content_list.html', {
        'contents': contents,
        'topics': topics,
        'subject': subject,
        'selected_topic_id': topic_id,
        'sidebar_subjects': sidebar_subjects,
    })




@login_required
def edit_content(request, pk):
    content = get_object_or_404(Content, pk=pk)
    sidebar_subjects = get_user_subjects(request.user) 
    # only its teacher may edit
    if request.user != content.teacher:
        messages.error(request, "Not permitted.")
        return redirect('contents:content_list')

    # fetch subject & topics for dropdown
    subject = content.subject
    topics = Topic.objects.filter(subject=subject, teacher=request.user)
    students = subject.students.all()

    if request.method == 'POST':
        # 1) basic fields
        content.title       = request.POST['title']
        content.description = request.POST['description']
        new_topic_name      = request.POST.get('new_topic', '').strip()
        topic_id            = request.POST.get('topic')

        # 2) topic logic
        if new_topic_name:
            topic = Topic.objects.create(
                topic_name=new_topic_name,
                subject=subject,
                teacher=request.user
            )
        else:
            topic = get_object_or_404(Topic, id=topic_id, subject=subject)
        content.topic = topic
        content.save()

        # 3) assigned students
        stu_ids = request.POST.getlist('students')
        content.assigned_to.set(stu_ids)

        # 4) remove checked files
        for fid in request.POST.getlist('remove_file'):
            cf = ContentFile.objects.filter(id=fid, content=content).first()
            if cf: cf.delete()
        # 5) add new uploads
        for f in request.FILES.getlist('new_files'):
            ContentFile.objects.create(
                content=content,
                file=f,
                mime_type=f.content_type.split('/')[0]
            )

        # 6) remove checked links
        for lid in request.POST.getlist('remove_link'):
            cl = ContentLink.objects.filter(id=lid, content=content).first()
            if cl: cl.delete()
        # 7) add/update links
        for url in request.POST.getlist('links'):
            u = url.strip()
            if u:
                ContentLink.objects.get_or_create(content=content, link=u)

        messages.success(request, "Content updated.")
        return redirect(f"{reverse('contents:content_list')}?subject={subject.id}")

    # GET: render form
    return render(request, 'contents/edit_content.html', {
        'content': content,
        'topics': topics,
        'students': students,
        'sidebar_subjects': sidebar_subjects,
    })




@login_required
def delete_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    # Optional: restrict access
    if request.user != content.teacher:
        return redirect('contents:content_list')

    subject = content.subject  # grab this now

    if request.method == 'POST':
        content.delete()
        # redirect back to the list of contents for that subject
        return redirect(f"{reverse('contents:content_list')}?subject={subject.id}")

    return render(request, 'contents/delete_content.html', {
        'content': content,
        'subject': subject,    # new
    })

@login_required
def view_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    sidebar_subjects = get_user_subjects(request.user) 
    raw_files = content.files.all()
    files = []
    for f in raw_files:
        files.append({
            'url':  f.file.url,
            'type': f.mime_type,
            'name': os.path.basename(f.file.name),
        })

    links = content.links.all()
    return render(request, 'contents/view_content.html', {
        'content': content,
        'files':    files,
        'links':    links,
        'sidebar_subjects': sidebar_subjects,
    })

