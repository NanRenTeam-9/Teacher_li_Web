from django.http import JsonResponse
from django.shortcuts import render
from jieba.analyse import extract_tags
from django.db.models import Q
from main_app import models
import string
import refresh
import time


# Create your views here.
def main_page(request):
    return render(request, "index.html")


def main_page2(request):
    refresh.update_details()  # 更新数据库疫情数据
    refresh.update_history()
    return render(request, "main.html")


def get_time(request):
    time_str = time.strftime("%Y{}%m{}%d{} %X")
    return JsonResponse(time_str.format("年", "月", "日"), safe=False)


def get_c1_data(request):
    data = models.history.objects.filter().order_by("ds").last()
    return JsonResponse({"confirm": data.confirm, "suspect": data.suspect, "heal": data.heal, "dead": data.dead},
                        safe=False)


def get_c2_data(request):
    res = []
    k = {}
    data = models.details.objects.all()
    update_time = models.details.objects.filter().order_by('update_time').last().update_time

    for i in data:
        if i.update_time == update_time:
            if i.province not in k.keys():
                k[i.province] = int(i.confirm)
            else:
                k[i.province] += int(i.confirm)

    for i in k.keys():
        res.append({'name': i, 'value': k[i]})

    return JsonResponse({"data": res}, safe=False)


def get_l1_data(request):
    data = models.history.objects.all()
    day, confirm, suspect, heal, dead = [], [], [], [], []
    for a in data:
        day.append(a.ds.strftime("%m-%d"))
        confirm.append(a.confirm)
        suspect.append(a.suspect)
        heal.append(a.heal)
        dead.append(a.dead)
    return JsonResponse({"day": day, "confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead}, safe=False)


def get_l2_data(request):
    data = models.history.objects.all().order_by('ds')
    day, confirm_add, suspect_add = [], [], []
    for idx, a in enumerate(data):
        day.append(a.ds.strftime("%m-%d"))  # a是datatime类型
        if idx == 0:
            confirm_add_num = 0
            suspect_add_num = 0
        else:
            confirm_add_num = a.confirm - data[idx - 1].confirm
            suspect_add_num = a.suspect - data[idx - 1].suspect

        confirm_add.append(confirm_add_num)
        suspect_add.append(suspect_add_num)

    return JsonResponse({"day": day, "confirm_add": confirm_add, "suspect_add": suspect_add}, safe=False)


def get_r1_data(request):
    data = models.details.objects.filter(~Q(province='湖北')).order_by('-confirm')
    update_time = models.details.objects.filter().order_by('update_time').last().update_time

    kk = {}
    city = []
    confirm = []

    not_confirm = 0
    out = 0

    for k in data:
        if k.update_time == update_time:
            if k.city == "地区待确认":
                not_confirm += int(k.confirm)
            elif k.city == "境外输入":
                out += int(k.confirm)
            else:
                city.append(k.city)
                confirm.append(int(k.confirm))
    city.append("地区待确认")
    city.append("境外输入")
    confirm.append(not_confirm)
    confirm.append(out)

    for i in range(len(city)):
        if city[i] not in kk.keys():
            kk[city[i]] = confirm[i]
        else:
            kk[city[i]] += confirm[i]

    kk = sorted(kk.items(), key=lambda item: item[1], reverse=True)

    top5_city = [i[0] for i in kk[:5]]
    top5_confirm = [i[1] for i in kk[:5]]

    return JsonResponse({"city": top5_city, "confirm": top5_confirm}, safe=False)


def get_r2_data(request):

    data = (('民警抗疫一线奋战16天牺牲1037364',), ('四川再派两批医疗队1537382',))  # 数据例子
    d = []
    for i in data:
        k = i[0].rstrip(string.digits)  # 移除热搜数字
        v = i[0][len(k):]  # 获取热搜数字
        ks = extract_tags(k)  # 使用jieba 提取关键字
        for j in ks:
            if not j.isdigit():
                d.append({"name": j, "value": v})

    return JsonResponse({"kws": d}, safe=False)
