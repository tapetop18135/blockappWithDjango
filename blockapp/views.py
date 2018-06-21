from django.shortcuts import render , get_object_or_404 
from django.http import HttpResponse , HttpResponseRedirect , Http404
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.db.models import Q


from .models import Blocktable
from .form import Blockform

def isLoginAndPermission(request):
    if(request.user.is_superuser):
        return {"isLogin" : True, "username" : "Super User : "+str(request.user)}
    if request.user.is_authenticated:
        return {"isLogin" : True, "username" : request.user}
    else :
        return {"isLogin" : False, "username" : ""}

def index(request):
    for key in request.session.keys():
        print(key)

    if(request.user.is_superuser):
        print("Admin")
        listBlock = Blocktable.objects.order_by('-date')
        print(listBlock)

    elif request.user.is_authenticated:
        print("have user")
        filterlist = Blocktable.objects.filter(Q(isPrivate=0) | Q(authId=request.session["_auth_user_id"]))
        
        print(filterlist)
        listBlock = filterlist.order_by('-date')
    else:
        print("Public")
        filterlist = Blocktable.objects.filter( isPrivate = 0)
        listBlock = filterlist.order_by('-date')
        print(listBlock)



    # print(type(filterlist))
    # listBlock = filterlist.order_by('-date')

    # listBlock = Blocktable.objects.order_by('-date')


    
    return render(request,'index.html',{"listblock" : listBlock, "login" : isLoginAndPermission(request) })
    # except:
    #     return render(request,'index.html',{"listblock" : listBlock, "login" : isLoginAndPermission(request) })

def showBlock(request, blockid):

    oneBlock = get_object_or_404(Blocktable, id=blockid)
    login = isLoginAndPermission(request)
    
    print(login)
    if((oneBlock.authId == isLoginAndPermission(request)["username"] and request.user.has_perm("blockapp.add_blocktable"))or request.user.is_superuser):
        login["canEdit"] = True
    else:
        login["canEdit"] = False

    print(login)
    return render(request,'detailOneBlock.html',{"blockone" : oneBlock , "login" : login })


def createBlockform(request):
    return render(request,'createBlockForm.html')

def creteBlock(request):
    if request.method  == "POST" :
        form = Blockform(request.POST)
        if form.is_valid():
            obj = Blocktable()
            obj.title = form.cleaned_data['title']
            obj.content = form.cleaned_data['content']
            obj.authId = request.user
            obj.save()
            return HttpResponseRedirect(reverse('blockapp:oneblock', args=(obj.id,)))
        return Http404("Error")
    else:        
        return Http404("Error")
    
def updateBlockForm(request, blockid):
    
    oneBlock = get_object_or_404(Blocktable, id=blockid)
    
    return render(request,'updateBlockForm.html',{"blockone" : oneBlock })


def updateBlock(request, blockid):
    if request.method == "POST":
        obj = Blocktable.objects.get(id=blockid)
        print(blockid)
        obj.title = request.POST.get("title")
        obj.content = request.POST.get("content")
        obj.save()

    return HttpResponseRedirect(reverse('blockapp:oneblock', args=(blockid,)))

def delete(request, blockid):
    block = get_object_or_404(Blocktable, id=blockid)
    block.delete()
    return HttpResponseRedirect(reverse('blockapp:index'))