import json
import re
from django.shortcuts import redirect, render
from django.http import JsonResponse, FileResponse
from .models import shortURL


import qrcode
import re
import io
from PIL import Image

rmve_bracket = "\(.*\)|\s-\s.*" 
remain_brakcet = r'\(([^)]+)'


# Create your views here.
def str2urlpath(reqstr):
    # 내부에서 영문 대소문자 구분하지않음(중복혼란방지)
    # 공백문자는 URL상에서 허용하지않기때문에 _(언더바)로 대치
    return reqstr.lower().replace(' ', '_')


def index(request):
    #['학생', '공용', '학부생', '대학원생', '교원', '직원']
    
    context = { 
        'count': shortURL.objects.count()
        }
        
    if request.user.is_authenticated:
        namestr = request.user.first_name
        context['name'] = re.sub(rmve_bracket, '', namestr)
        try:
            context['badge'] = re.findall(remain_brakcet, namestr)[0]
        except:
            context['badge'] = ''

    return render(request, 'index.html', context)


def create(request):
    if request.method == 'POST' and request.user.is_authenticated:
        print(json.loads(request.body))
        req_data = json.loads(request.body)
        path = str2urlpath(req_data['path_word'])
        url = req_data['url']
        #중복확인
        try:
            shortURL.objects.get(path_word=path)
            result = { 'result': 'fail',
                        'data': 'already_exist'}
            print(result)
            return JsonResponse(result)
        except:
            shortURL(path_word=path, url=url, creater=request.user).save()
            result = { 'result': 'success',
                        'data': req_data['path_word'].replace(' ', '_')}
            print(result)
            return JsonResponse(result)
    else:
        result = { 'result': 'fail',
                    'data': 'wrong_access'}
        print(result)
        return JsonResponse(result)


def edit(request):
    if request.method == 'PUT' and request.user.is_authenticated:
        print(json.loads(request.body))
        req_data = json.loads(request.body)
        path = str2urlpath(req_data['path_word'])
        url = req_data['url']
        try:
            short = shortURL.objects.get(path_word=path)
            if short.creater != request.user:
                raise Exception('permission_denied')
            short.url = url
            short.save()

            result = { 'result': 'success',
                        'data': shortURL.objects.get(path_word=path).url}
            print(result)
            return JsonResponse(result)
        except Exception as e:
            print(e)
            result = { 'result': 'fail',
                        'data': 'wrong_access'}
            print(result)
            return JsonResponse(result)
    else:
        result = { 'result': 'fail',
                    'data': 'wrong_access'}
        print(result)
        return JsonResponse(result)


def delete(request):
    if request.method == 'DELETE' and request.user.is_authenticated:
        print(json.loads(request.body))
        req_data = json.loads(request.body)
        path = str2urlpath(req_data['path_word'])
        try:
            short = shortURL.objects.get(path_word=path)
            if short.creater != request.user:
                raise Exception('permission_denied')
            short.delete()
            
            result = { 'result': 'success'}
            print(result)
            return JsonResponse(result)
        except Exception as e:
            print(e)
            result = { 'result': 'fail',
                        'data': 'wrong_access'}
            print(result)
            return JsonResponse(result)
    else:
        result = { 'result': 'fail',
                    'data': 'wrong_access'}
        print(result)
        return JsonResponse(result)


def qr(request, path_word):
    Logo_link = 'kmu.jpg'
    logo = Image.open(Logo_link)
    
    # taking base width
    basewidth = 100
    
    # adjust image size
    wpercent = (basewidth/float(logo.size[0]))
    hsize = int((float(logo.size[1])*float(wpercent)))
    logo = logo.resize((basewidth, hsize), Image.ANTIALIAS)
    QRcode = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    
    # taking url or text
    url = f'http://kmu.ac/{path_word}?ref=QR'
    
    # adding URL or text to QRcode
    QRcode.add_data(url)
    
    # generating QR code
    QRcode.make()

    
    # adding color to QR code
    QRimg = QRcode.make_image(fill_color=(0, 79, 159), back_color="white")
    
    # set size of QR code
    pos = ((QRimg.size[0] - logo.size[0]) // 2,
        (QRimg.size[1] - logo.size[1]) // 2)
    QRimg.paste(logo, pos)
    
    # save the QR code generated
    QRimg.save('temp.png')
    
    return FileResponse(open('temp.png', 'rb'))


def mypage(request):
    if request.user.is_authenticated:
        urls = shortURL.objects.filter(creater= request.user)
        context = {'urls': urls}
        namestr = request.user.first_name
        context['name'] = re.sub(rmve_bracket, '', namestr)
        try:
            context['badge'] = re.findall(remain_brakcet, namestr)[0]
        except:
            context['badge'] = ''

        return render(request, 'mypage.html', context)
    else:
        return redirect('/')



def not_found(request):
    context = { 
        'count': shortURL.objects.count()
        }
    if request.user.is_authenticated:
        namestr = request.user.first_name
        context['name'] = re.sub(rmve_bracket, '', namestr)
        try:
            context['badge'] = re.findall(remain_brakcet, namestr)[0]
        except:
            context['badge'] = ''
    return render(request, 'notfound.html', context)


def mapping(request, path_word):
    try:
        return redirect(shortURL.objects.get(path_word=str2urlpath(path_word)).url)
    except:
        return redirect('/not_found')