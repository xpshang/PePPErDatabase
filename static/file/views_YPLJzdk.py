from django.http import HttpResponse, JsonResponse

from django.db import transaction
from django.views import View
from classApp.models import ClassType, ClassUser, Classinfo, ClassUserExerciseInfo
from userApp.models import UserInfo as User
from userApp.models import UserRankInfo
from .models import ExerciseGroup, ExerciseRelationGroup, Exercise
from exerciseApp.models import UserExerciseRecord, UserExercise, DurationProblem
from onlinejudgeApp.views import addTestCase, addproblem, delproblem
from auth import *
cache = ConnectionProxy(caches, "snowflake")
from onlinejudgeApp.models import ProblemDetail, SampleDetail
from exerciseApp.models import CopyRank
from rest_framework.views import APIView
from rest_framework.response import Response

from core.classOption.classExercise import addExerciseToUser
import random

import oss2
class ExerciseDetailView(View):
    def get(self, request):
        id = request.GET.get("id")

        data = {}
        exerciseAll = Exercise.objects.get(id=id)
        if str(exerciseAll.source_type) == "3":
            data['mark'] = 0
            exercise = ProblemDetail.objects.get(id=id)
            data['can_test'] = exerciseAll.can_test
            data['title'] = exercise.title
            data['description'] = exercise.description
            data['input_description'] = exercise.input_description
            data['output_description'] = exercise.output_description
            data['memory_limit'] = exercise.memory_limit
            data['time_limit'] = exercise.time_limit
            data['output_description'] = exercise.output_description
            data['output_description'] = exercise.output_description
            data['hintInfo'] = exercise.hint
            data['id'] = exercise.id
            samplelist = SampleDetail.objects.filter(problem_detail_id=id)
            list = []
            for sample in samplelist:
                dict1 = {}
                dict1['input'] = sample.input
                dict1['output'] = sample.output
                list.append(dict1)
            data['sample_list'] = list
        else:

            data = {}
            data['can_test'] = exerciseAll.can_test
            data['mark'] = 1

            exercise = Exercise.objects.get(id=id)
            data['id'] = exercise.id
            if exercise.content == None or exercise.content == "":
                try:
                    exercise = ProblemDetail.objects.get(id=id)
                    content = exercise.content
                except:
                    content = "<div>暂无</div>"
            else:
                content = exercise.content.replace("<div/>", "无</div>")
            data['content'] = content
            data['title'] = exercise.title
            data['id'] = exercise.id
        return JsonResponse({"code": 1, "data": data})


from django.db import connection


class ExerciseView(View):
    def get(self, request):
        sql = "select id,title from exercise"

        cursor = connection.cursor()
        cursor.execute(sql)
        exerciselst = cursor.fetchall()
        data = []
        data2 = []
        for i in exerciselst:
            dict1 = {}
            dict1['key'] = i[0]
            dict1['label'] = i[1]
            dict1['desc'] = None
            data.append(dict1)
            data2.append(i[0])
        return JsonResponse({"code": 1, "data": {"value": data, "key": data2}})


class ShowCode(View):
    def get(self, request):
        id = request.GET.get("id")
        user_id = request.GET.get("user_id")
        classid = request.GET.get("classid")
        userExercise = UserExerciseRecord.objects.filter(exercise_id=id).filter(user_id=user_id).last()

        result = {}
        if userExercise is not None:
            result["code"] = userExercise.code
            result["id"] = userExercise.id
        classUserExercise = ClassUserExerciseInfo.objects.filter(user_id=user_id).filter(exercise_id=id).filter(
            class_id=classid).first()
        if classUserExercise is not None:
            if classUserExercise.is_reset == 1:

                result["is_reset"] = True
            else:
                result['is_reset'] = False
            if classUserExercise.is_copy == 1:

                result["is_copy"] = True
            else:
                result["is_copy"] = False

        userlist = UserExerciseRecord.objects.filter(exercise_id=id).filter(user_id=user_id).order_by("-create_time")
        recordlist = []
        for i in userlist:
            dict1 = {}
            dict1["id"] = i.id
            dict1["code"] = i.code
            if i.duration == None:
                dict1['duration'] = ""
            else:
                dict1['duration'] = int(round(i.duration / 60))
            create_time = str(i.create_time)
            dict1['create_time'] = create_time[5:10] + " " + create_time[11:16] + " 星期 " + str(
                i.create_time.isoweekday())
            dict1['score'] = i.score
            recordlist.append(dict1)
        username = UserInfo.objects.get(id=user_id).username
        problemName = Exercise.objects.get(id=id).title
        result['username'] = username
        result['problemName'] = problemName
        result['recordlist'] = recordlist
        return JsonResponse({"code": 1, "data": result})


class TeacherListView(View):
    def get(self, request):

        keyword = request.GET.get("keyword")
        teacherList = User.objects.filter(state=1)
        if keyword is not None:
            teacherList = teacherList.filter(username=keyword)
        resultTeacher = []

        for i in teacherList:
            teacherDict = {}
            teacherDict["id"] = i.id
            teacherDict["username"] = i.username
            resultTeacher.append(teacherDict)
        return JsonResponse({"code": 1, "data": resultTeacher})


class TypeListView(View):

    def get(self, request):
        # 从缓存中获取用户名和权限
        try:
            loginId = request.GET.get("loginId")
            userid = cache.get(loginId)
            user_id, state = userid.split("_")
        except:
            return JsonResponse({"code":1,"data":[]})
        result = []
        # 由于是后来新加的需求，之前没有create_user字段，所以在增加create_user字段时，create_user设置了为0
        # 如果类型为2为超级管理员模式，设置user_id 为0
        if state == "2":
            user_id = 0
            # 查询出登录用户所创建的班级类型
            tyList = ClassType.objects.filter(create_user=user_id).order_by("-id")
            for i in tyList:
                dict1 = {}
                dict1['id'] = i.id
                dict1["name"] = i.name
                result.append(dict1)
        else:
            tyList_teacher = ClassType.objects.filter(create_user=user_id).order_by("-id")
            tyList_super = ClassType.objects.filter(create_user=0).order_by("-id")
            for j in tyList_teacher:
                dict2 = {}
                dict2['id'] = j.id
                dict2["name"] = j.name
                result.append(dict2)
            for n in tyList_super:
                dict3 = {}
                dict3['id'] = n.id
                dict3["name"] = n.name
                result.append(dict3)
        return JsonResponse({"code": 1, "data": result})


class IndexView(View):
    def get(self, request):
        loginId = request.GET.get("loginId")

        try:
            user = cache.get(loginId)
            user_id, user_role = user.split("_")
        except:

            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})

        year = request.GET.get("year", None)
        classType = request.GET.get("classType", None)
        season = request.GET.get("season", None)
        teacherId = request.GET.get("teacher", None)
        searchType = request.GET.get("searchType", None)
        keyword = request.GET.get("keyword", None)
        if searchType is None and int(user_role) == 1:
            teacherId = user_id

        # 查询所有的班级信息
        sql = """SELECT
	c.id AS id,
	c.teacherName AS teacherName,
	c.className AS className,
	c.season AS season,
	c.YEAR AS YEAR,
	t.NAME AS classTypeName,
	t.id AS classTypeId ,
	c.classroom AS classroom ,
	c.code AS code 
FROM
	classinfo AS c
	LEFT JOIN class_type AS t ON t.id = c.classType where 1=1"""
        if searchType is not None and searchType != "":
            if str(searchType) == '1':
                if year is not None and year != "":
                    sql += " and  c.year =" + year
                if classType is not None and classType != "":
                    sql += " and t.id = " + classType
                if season is not None and season != "":
                    sql += " and c.season = " + season
                if teacherId is not None and teacherId != "":
                    sql += " and c.teacherId = " + teacherId
            elif str(searchType) == '2':
                sql += " and c.name like '%" + keyword + "%' "
        elif int(user_role) == 1:
            sql += " and c.teacherId = " + teacherId
        sql += " ORDER By id DESC"
        cursor = connection.cursor()

        cursor.execute(sql)

        classInfo = cursor.fetchall()
        if len(classInfo) == 0:
            return JsonResponse({"code": 1, "data": []})
        classIdList = [x[0] for x in classInfo if x[0] is not None]

        classIdList = str(tuple(set(classIdList)))
        if classIdList[-2] == ",":
            classIdList = classIdList[0:-2] + ")"

        # 根据class_id,班级，然后每个班级按groupID排序，数据库是class_relation_group

        sql = """SELECT
	crg.class_id,
	crg.group_id,
	crg.is_now,
	eg.`name`,
	IFNULL(eg.score,0),
	IFNULL(eg.base_score,0),
	IFNULL(eg.challege_score,0),
	crg.order_desc
FROM
	class_relation_group AS crg
	LEFT JOIN exercise_group AS eg ON crg.group_id = eg.id  
WHERE
	crg.class_id IN %s 
ORDER BY
	crg.order_desc""" % classIdList
        cursor.execute(sql)
        classAndGroupList = cursor.fetchall()

        result = {}
        for i in classInfo:
            detail = {}
            detail['id'] = i[0]
            detail["score"] = 0
            detail["base_score"] = 0
            detail["chanllege_score"] = 0
            detail['teacherName'] = i[1]
            detail['className'] = i[2]
            detail['season'] = i[3]
            detail['year'] = i[4]
            detail['typeName'] = i[5]
            detail['classroom'] = i[7]
            detail['code'] = i[8]
            detail['groupList'] = []
            detail['groupIdList'] = []
            detail['userScore'] = []

            result[i[0]] = detail
        # title 列表
        for i in classAndGroupList:
            # 如果该id不在符合的学生列表中则进行下一个
            if i[0] not in result.keys():
                continue
            detail = {}
            if i[3] is None:
                groupName = ""
            elif len(i[3]) > 9:
                groupName = i[3][0:9]
            else:
                groupName = i[3]
            detail['groupName'] = groupName
            detail['groupId'] = i[1]
            detail['score'] = i[4]
            detail['base_score'] = i[5]
            detail['chanllege_score'] = i[6]

            if i[2] == 0:
                detail['is_now'] = False
            else:
                detail['is_now'] = True

            detail['orderDesc'] = i[7]
            detail['classId'] = i[0]
            result[i[0]]['groupList'].append(detail)
            result[i[0]]['groupIdList'].append(i[1])
            result[i[0]]["grouplength"] = len(result[i[0]]['groupIdList']) * 200 + 485
            result[i[0]]["score"] += i[4]
            result[i[0]]["base_score"] += i[5]
            result[i[0]]["chanllege_score"] += i[6]

        # 获取class

        sql = """SELECT
	sum( if(score!=-1 and question_finish=1,score,0) ) AS score,
	sum(
	IF
	( is_challege = 1 and score!=-1 and question_finish=1, score, 0 )) AS challege_score,
		sum(
	IF
	( is_challege = 0 and score!=-1  and question_finish=1, score, 0 )) AS base_score,
	class_id,
	group_id,
	user_id,
	class_user_exercise_info.id ,
	username,
	user_info.tip,
	user_info.rank
FROM
	class_user_exercise_info left join user_info on user_info.id=class_user_exercise_info.user_id
WHERE
	 class_id in %s
GROUP BY
	user_id,
	group_id,
	class_id""" % classIdList
        cursor.execute(sql)
        userScoreList = cursor.fetchall()
        scoreClassDict = {}

        for userSocre in userScoreList:
            # 第一次创建班级并初始化字典
            groupIdList = result[userSocre[3]]['groupIdList']
            if userSocre[8] == "" or userSocre[8] is None:
                tip = False
            else:
                tip = userSocre[8]

            if userSocre[3] not in scoreClassDict.keys():
                groupScoreList = []

                for i in groupIdList:
                    groupScoreList.append(False)
                try:
                    groupScoreList[groupIdList.index(userSocre[4])] = userSocre[0]
                except Exception as e:
                    continue
                # 创建一条记录
                scoreClassDict[userSocre[3]] = {
                    userSocre[5]: {"user_name": userSocre[7], "user_id": userSocre[5], "base_socre": userSocre[2],
                                   "challege_score": userSocre[1], "score": userSocre[0], "tip": tip,
                                   "rank": userSocre[9],
                                   "group_score": groupScoreList}}
            else:
                if userSocre[5] not in scoreClassDict[userSocre[3]].keys():
                    groupScoreList = []

                    for i in groupIdList:
                        groupScoreList.append(False)
                    if userSocre[4] is None:
                        continue

                    groupScoreList[groupIdList.index(userSocre[4])] = userSocre[0]

                    scoreClassDict[userSocre[3]][userSocre[5]] = {"user_name": userSocre[7], "user_id": userSocre[5],
                                                                  "base_socre": userSocre[2],
                                                                  "challege_score": userSocre[1], "score": userSocre[0],
                                                                  "group_score": groupScoreList, "tip": tip,
                                                                  "rank": userSocre[9]}
                else:

                    scoreClassDict[userSocre[3]][userSocre[5]]["challege_score"] += userSocre[1]
                    scoreClassDict[userSocre[3]][userSocre[5]]["base_socre"] += userSocre[2]
                    scoreClassDict[userSocre[3]][userSocre[5]]["score"] += userSocre[0]
                    scoreClassDict[userSocre[3]][userSocre[5]]["group_score"][(groupIdList.index(userSocre[4]))] = \
                        userSocre[0]
        data = []
        for key, value in result.items():

            # 成绩里没有，但是学生有的数据
            if key in scoreClassDict.keys():
                # try:

                userScoreDetail = sorted(list(scoreClassDict[key].values()), key=lambda x: x['score'], reverse=True)
                # except:
                #     continue
                dict1 = value
                dict1['userScore'] = userScoreDetail
                data.append(dict1)
            else:
                dict1 = value
                dict1["userScore"] = []
                data.append(dict1)
        return JsonResponse({"code": 1, "data": data})


# 优化sql
import datetime


# 修改升级天数
class EditDay(View):
    def get(self, request):
        authInfo = LoginAuth(request, (2,))
        if authInfo == False:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})

        day = request.GET.get("day")
        try:
            day = int(day)
        except:
            return JsonResponse({"code": -1, "message": "数据不对"})

        config = Config.objects.get(key="rank_day")
        config.value = day
        config.save()
        return JsonResponse({"code": 1, "message": "保存成功"})


# 修改某一个学生分数

class EditScoreAdmin(View):
    def get(self, request):
        authInfo = LoginAuth(request, (1, 2,))
        if authInfo == False:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})

        score = request.GET.get("score")
        user_id = request.GET.get("user_id")
        try:
            userRankInfo = UserRankInfo.objects.get(user_id=user_id)
        except:
            UserRankInfo.objects.create(user_id=user_id, adminscore=score, yesscore=0, day=0,
                                        create_day=datetime.datetime.today(), isupdate=1)
            return JsonResponse({"code": 1, 'message': "succeed"})

        try:
            score = float(score)
        except:
            return JsonResponse({"code": -3, 'message': "数据错误"})

        userRankInfo.adminscore += score
        userRankInfo.save()
        return JsonResponse({"code": 1, 'message': "succeed"})


class StatisView(View):
    def get(self, request):
        loginId = request.GET.get('loginId')
        range2 = request.GET.get("range")

        try:
            user = cache.get(loginId)
            user_id, user_role = user.split("_")
        except:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})
        daysHave = None
        if int(user_role) == 0:
            classInfo = ClassUser.objects.filter(user_id=user_id).last()

            if classInfo is not None:

                classId = classInfo.class_id
                daysHave = UserRankInfo.objects.get(user_id=user_id).day
            else:
                return JsonResponse({"code": -2, 'message': "没有该班级"})

        else:
            class_id = request.GET.get("id")
            if class_id is None or class_id == "":
                return JsonResponse({"code": -2, 'message': "没有该班级"})
            classId = class_id

        # classId=578
        # range2=2

        # 查询一年以内的，然后
        # 先查询出来每日的
        sql = """

select * from (


select ifnull(s.score,0),u.username,u.id as id,ifnull(s.day,now()) as day,u.`rank`,ifnull(uri.adminScore,0),ifnull(uri.yesScore,0)  from score_daily as s right join class_user cu on s.user_id = cu.user_id left join user_info as u on u.id=cu.user_id left join user_rank_info uri on cu.user_id = uri.user_id where cu.class_id=%s) as f order by f.id,f.day        """
        cursor = connection.cursor()
        cursor.execute(sql % classId)
        scoreList = cursor.fetchall()
        userScore = {}
        for i in scoreList:
            if i[2] not in userScore.keys():
                (i[4] / 10 + 1) * i[5]
                userScore[i[2]] = {"username": i[1], "user_id": i[2], "rank": i[4], "adminScore": i[5],
                                   "base_score": i[6],
                                   "rank_rate": i[4] / 10 + 1,
                                   "scoreDict": {datetime.datetime.strftime(i[3], '%Y-%m-%d'): i[0]}, "x": [], "y": [],
                                   "start_time": i[3]}
            else:
                userScore[i[2]]["scoreDict"][datetime.datetime.strftime(i[3], '%Y-%m-%d')] = i[0]

        # 获取天数，把每个日期拿到做一个列表，然后从这个列表里面进行移动游标取值
        today = datetime.datetime.today()
        xindex = []
        if int(range2) == 0:
            days = 15
        elif int(range2) == 1:
            days = 30
        elif int(range2) == 2:
            days = 90
        elif int(range2) == 3:
            days = 180
        else:
            days = None
        if days is not None:
            for x in range(days, -1, -1):
                days = today + datetime.timedelta(days=-x)  # 减去一天
                xindex.append(datetime.datetime.strftime(days, '%Y-%m-%d'))
        result = []

        for key, value in userScore.items():
            resultDict = {}
            resultDict["username"] = value["username"]
            resultDict["user_id"] = value["user_id"]
            resultDict["rank"] = value["rank"]
            resultDict["adminScore"] = value["adminScore"]
            resultDict["base_score"] = value["base_score"]
            resultDict["rank_rate"] = value["rank_rate"]
            current_score = 0
            scoreEndlist = []

            if days is None:
                start_time = value["start_time"]
                days = int(str(datetime.datetime.today() - start_time).split("days")[0].strip())
                for x in range(days, -1, -1):
                    days = today + datetime.timedelta(days=-x)  # 减去一天
                    xindex.append(datetime.datetime.strftime(days, '%Y-%m-%d'))

            for i in value["scoreDict"].keys():
                if i > xindex[0]:
                    break
                current_score = value["scoreDict"][i]
            for i in xindex:

                if i in value['scoreDict'].keys():
                    current_score = value["scoreDict"][i]
                scoreEndlist.append(current_score)
            resultDict["x"] = xindex
            resultDict["y"] = scoreEndlist
            result.append(resultDict)

        config = Config.objects.get(key="rank_day")
        day = config.value
        if daysHave is not None:
            need_day = int(day) - int(daysHave)
        else:
            need_day = False

        return JsonResponse({"code": 1, "data": result, "day": day, "need_day": need_day})


class ClassListForStudent(View):
    def get(self, request):
        loginId = request.GET.get('loginId')
        try:
            user = cache.get(loginId)
            user_id, user_role = user.split("_")
        except:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})
        if int(user_role) == 0:
            result = []
            classUser = ClassUser.objects.filter(user_id=user_id).all()
            for i in classUser:
                try:
                    classinfo = Classinfo.objects.get(id=i.class_id)
                    result.append({"id": classinfo.id, "name": classinfo.classname})
                except:
                    continue
            return JsonResponse({"code": 1, "data": result})
import time

class ClassDeatil(View):
    def get(self, request):
        start_time = time.time()

        loginId = request.GET.get('loginId')
        try:
            user = cache.get(loginId)
            user_id, user_role = user.split("_")
        except:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})

        if int(user_role) == 0:
            class_id = request.GET.get("id")
            if class_id is None or class_id == "":
                classInfo = ClassUser.objects.filter(user_id=user_id).last()
                if classInfo is not None:
                    classId = classInfo.class_id
                else:
                    return JsonResponse({"code": -2, 'message': "没有该班级"})

            else:
                classId = class_id

        else:
            refresh = request.GET.get('refresh')
            class_id = request.GET.get("id")
            if class_id is None or class_id == "":
                return JsonResponse({"code": 1, "status": 1, "message": "没有班级"})

            classId = class_id
            if refresh == "1":
                ScoreIsUpdate = cache.get("class_score_update_" + str(classId) + "_" + str(user_id))
                if ScoreIsUpdate is not None and ScoreIsUpdate == False:
                    return JsonResponse({"code": 1, "status": 1, "message": "还未更新"})
                else:
                    cache.set("class_score_update_" + str(classId) + "_" + str(user_id), False, 10)

        try:
            classInfo = Classinfo.objects.get(id=classId)
        except Exception as  e:
            print(e)
            return JsonResponse({"code": -2, 'message': "没有该班级"})
        end_time=time.time()
        print("阶段一耗时：",end_time-start_time)
        start_time=time.time()

        result = {}
        result["name"] = classInfo.classname
        result['id'] = classInfo.id

        try:
            classInfoType = ClassType.objects.get(id=classInfo.classtype)
        except:
            return JsonResponse({"code": -2, 'message': "不存在班级类型"})

        result["type"] = classInfoType.name
        result["link"] = classInfoType.link
        result["teacherName"] = User.objects.get(id=classInfo.teacherid).username
        if result['link'] == "" or result["link"] is None:
            result['link'] = False

        cursor = connection.cursor()

        sql = """SELECT
	crg.class_id,
	crg.group_id,
	crg.is_now,
	eg.`name`,
	ifnull(eg.score,0),
	ifnull(eg.base_score,0),
	ifnull(eg.challege_score,0),
	crg.order_desc
FROM
	class_relation_group AS crg
	LEFT JOIN exercise_group AS eg ON crg.group_id = eg.id 
WHERE
	crg.class_id = %s
ORDER BY
	crg.is_now desc,
	crg.order_desc""" % classId

        # 获取所有的分组信息

        cursor.execute(sql)
        groupTitleList = cursor.fetchall()
        result["score"] = 0
        result['base_score'] = 0
        result["challege_score"] = 0
        result["groupList"] = []
        groupIdList = []
        end_time=time.time()
        print("阶段二耗时：",end_time-start_time)
        start_time = time.time()

        for i in groupTitleList:
            if result['score'] is not None:
                result["score"] += i[4]
                result["base_score"] += i[5]
                result["challege_score"] += i[6]
            if i[2] == 0:
                is_now = False
            else:
                is_now = True
            if i[3] is None:
                group_name = ""
            elif len(i[3]) > 9:
                group_name = i[3][0:9]
            else:
                group_name = i[3]
            dict1 = {"group_id": i[1], "group_name": group_name, "score": i[4], "base_score": i[5],
                     "challege_score": i[6],
                     "is_now": is_now}
            groupIdList.append(i[1])
            result["groupList"].append(dict1)
            result["base_score"] += i[5]
            result["challege_score"] += i[6]
            result["score"] += i[4]
            result["grouplength"] = len(result["groupList"]) * 200 + 485
        end_time = time.time()
        print("阶段三耗时：", end_time - start_time)
        start_time = time.time()
        sql = """SELECT
        	sum( if(score!=-1  and question_finish=1,score,0) ) AS score,
        	sum(
        	IF
        	( is_challege = 1 and score!=-1 and question_finish=1, score, 0 )) AS challege_score,
        		sum(
        	IF
        	( is_challege = 0 and score!=-1  and question_finish=1, score, 0 )) AS base_score,
        	group_id,
        	user_id,
        	class_user_exercise_info.id ,
        	username,
        	user_info.rank,
        	user_info.tip
        FROM
        	class_user_exercise_info left join user_info on user_info.id=class_user_exercise_info.user_id
        WHERE
        	 class_id = %s
        GROUP BY
        	user_id,
        	group_id""" % classId
        cursor.execute(sql)
        userScoreList = cursor.fetchall()
        groupScoreList = {}
        end_time = time.time()
        print("阶段四耗时：", end_time - start_time)
        start_time = time.time()
        for i in userScoreList:
            if i[4] not in groupScoreList.keys():
                scoreList = []
                allScore = int(i[0])
                baseScore = int(i[2])
                challengeScore = int(i[1])

                for x in groupIdList:
                    scoreList.append(False)
                if i[8] == "" or i[8] is None:
                    tip = False
                else:
                    tip = i[8]
                try:
                    scoreList[groupIdList.index(i[3])] = i[0]
                except:
                    continue
                groupScoreList[i[4]] = {"user_id": i[4], 'user_name': i[6], "id": i[5], "score": scoreList,
                                        'all_score': allScore, 'base_score': baseScore, "tip": tip, "rank": i[7],
                                        'challenge_score': challengeScore}
            else:
                groupScoreList[i[4]]['score'][groupIdList.index(i[3])] = i[0]
                groupScoreList[i[4]]['all_score'] += i[0]
                groupScoreList[i[4]]['challenge_score'] += i[1]
                groupScoreList[i[4]]['base_score'] += i[2]
        end_time = time.time()
        print("阶段五耗时：", end_time - start_time)
        start_time = time.time()
        groupScoreList = list(groupScoreList.values())
        groupScoreList = sorted(groupScoreList, key=lambda x: x['all_score'], reverse=True)
        end_time = time.time()
        print("阶段六耗时：", end_time - start_time)
        start_time = time.time()

        result["groupScoreInfo"] = groupScoreList
        if len(groupIdList)==1:
            groupIdList2=str(tuple(groupIdList)).replace(",","")
        else:
            groupIdList2 = str(tuple(groupIdList))


        sql = """SELECT
	erg.groupId,
	e.id,
	e.title,
	erg.isChallenge
FROM
	exercise_relation_group AS erg
	LEFT JOIN exercise AS e ON e.id = erg.exerciseId
WHERE
	erg.groupId IN %s
ORDER BY
	erg.orderDesc""" % (groupIdList2)

        if len(groupIdList) == 0:
            exerciseTitleList = []
        else:

            cursor.execute(sql)
            exerciseTitleList = cursor.fetchall()

        detailList = []
        titleDict = {}
        end_time = time.time()
        print("阶段七耗时：", end_time - start_time)
        start_time = time.time()
        for i in exerciseTitleList:
            if i[2] is None:
                title = ""
            elif len(i[2]) > 9:
                title = i[2][0:8] + '...'
            else:
                title = i[2]
            if i[0] not in titleDict.keys():

                if i[3] == 0:

                    base_titleId = []
                    base_title = [{"title": title, "id": i[1]}]
                    challenge = []
                    challengeId = []
                    base_titleId.append(i[1])
                else:
                    base_title = []
                    challengeId = []
                    base_titleId = []
                    challenge = [{"title": title, "id": i[1]}]
                    challengeId.append(i[1])
                titleDict[i[0]] = {"groupId": i[0], "base_title": base_title, "challenge": challenge,
                                   "challengeId": challengeId, "baseId": base_titleId}
            else:
                if i[3] == 1:
                    titleDict[i[0]]["challenge"].append({"title": title, "id": i[1]})
                    titleDict[i[0]]["challengeId"].append(i[1])

                else:
                    titleDict[i[0]]["base_title"].append({"title": title, "id": i[1]})
                    titleDict[i[0]]["baseId"].append(i[1])
            titleDict[i[0]]["exerciseLength"] = (len(titleDict[i[0]]["baseId"]) + len(
                titleDict[i[0]]["challengeId"])) * 200 + 485

        #  查询出出来的学生详情成绩
        end_time = time.time()
        print("阶段八耗时：", end_time - start_time)
        start_time = time.time()

        sql = """SELECT
	user_id,
	exercise_id,
	is_reset,
	is_copy,
	remark,
	is_challege,
	group_id,
	user_info.username,
	if(question_finish=1,score,-1) as score,
	cuei.id,
	user_info.tip,
	user_info.rank
FROM
	class_user_exercise_info AS cuei
	LEFT JOIN user_info ON user_info.id = cuei.user_id
WHERE

	 class_id = %s""" % classId

        cursor.execute(sql)
        userScoreList = cursor.fetchall()
        userScoreDict = {}
        end_time = time.time()
        print("阶段九耗时：", end_time - start_time)
        start_time = time.time()
        for i in userScoreList:
            baseId = titleDict[i[6]]['baseId']
            challengeId = titleDict[i[6]]['challengeId']
            if i[10] == None or i[10] == "":
                tip = False
            else:
                tip = i[10]

            if i[6] not in userScoreDict.keys():
                base_score_list = []
                challenge_score_list = []
                for x in baseId:
                    base_score_list.append("未完成")
                for x in challengeId:
                    challenge_score_list.append("未完成")
                if i[8] == -1:
                    score = False
                else:
                    score = i[8]

                if i[1] in baseId:
                    base_score_list[baseId.index(i[1])] = {"score": score, "is_reset": i[2], "is_copy": i[3],
                                                           "remark": i[4], 'id': i[9], "exerciseId": i[1]}
                else:
                    challenge_score_list[challengeId.index(i[1])] = {"score": score, "is_reset": i[2], "is_copy": i[3],
                                                                     "remark": i[4], 'id': i[9], "exerciseId": i[1]}
                if i[5] == 0:
                    challenge_score = 0
                    if i[8] != -1:
                        base_score = i[8]
                    else:
                        base_score = 0
                else:
                    base_score = 0
                    if i[8] != -1:
                        challenge_score = i[8]
                    else:
                        challenge_score = 0
                if i[8] != -1:
                    score = i[8]
                else:
                    score = 0
                userScoreDict[i[6]] = {i[0]: {"user_name": i[7], "challenge_score_list": challenge_score_list,
                                              "base_score_list": base_score_list, "user_id": i[0], "score": score,
                                              "base_score": base_score, "challenge_score": challenge_score, 'tip': tip,
                                              'rank': i[11]}}
            else:
                if i[0] not in userScoreDict[i[6]].keys():
                    base_score_list = []
                    challenge_score_list = []
                    for x in baseId:
                        base_score_list.append("未完成")
                    for x in challengeId:
                        challenge_score_list.append("未完成")
                    if i[8] == -1:
                        score = False
                        score2 = 0
                    else:
                        score = i[8]
                        score2 = i[8]
                    if i[1] in baseId:
                        base_score_list[baseId.index(i[1])] = {"score": score, "is_reset": i[2], "is_copy": i[3],
                                                               "remark": i[4], 'id': i[9], "exerciseId": i[1]}
                    else:
                        challenge_score_list[challengeId.index(i[1])] = {"score": score, "is_reset": i[2],
                                                                         "is_copy": i[3], "remark": i[4], 'id': i[9],
                                                                         "exerciseId": i[1]}
                    if i[5] == 0:
                        challenge_score = 0
                        if i[8] != -1:

                            base_score = i[8]
                        else:
                            base_score = 0
                    else:
                        if i[8] != -1:

                            challenge_score = i[8]
                        else:
                            challenge_score = 0
                        base_score = 0

                    userScoreDict[i[6]][i[0]] = {"user_name": i[7], "challenge_score_list": challenge_score_list,
                                                 "base_score_list": base_score_list, "user_id": i[0], "score": score2,
                                                 "base_score": base_score, "challenge_score": challenge_score,
                                                 'tip': tip, 'rank': i[11]}
                else:
                    if i[8] == -1:
                        score = 0
                        score2 = False
                    else:
                        score = i[8]
                        score2 = i[8]
                    userScoreDict[i[6]][i[0]]["score"] += score
                    if i[5] == 0:
                        userScoreDict[i[6]][i[0]]["base_score"] += score
                        userScoreDict[i[6]][i[0]]["base_score_list"][baseId.index(i[1])] = {"score": score2,
                                                                                            "is_reset": i[2],
                                                                                            "is_copy": i[3],
                                                                                            "remark": i[4], 'id': i[9],
                                                                                            "exerciseId": i[1]}
                    else:
                        userScoreDict[i[6]][i[0]]["challenge_score"] += score
                        userScoreDict[i[6]][i[0]]["challenge_score_list"][challengeId.index(i[1])] = {"score": score2,
                                                                                                      "is_reset": i[2],
                                                                                                      "is_copy": i[3],
                                                                                                      "remark": i[4],
                                                                                                      'id': i[9],
                                                                                                      "exerciseId": i[
                                                                                                          1]}
        end_time = time.time()
        print("阶段10耗时：", end_time - start_time)
        start_time = time.time()
        for i in groupTitleList:

            if i[2] == 0:
                is_now = False
            else:
                is_now = True
            try:

                scoreList = sorted(list(userScoreDict[i[1]].values()), key=lambda x: x['score'], reverse=True)
            except:
                continue

            detailDict = {"group_id": i[1], "group_name": i[3], "score": i[4], "base_score": i[5],
                          "challege_score": i[6],
                          "is_now": is_now, "challenge_title": titleDict[i[1]]["challenge"],
                          "base_title": titleDict[i[1]]["base_title"], "score_list": scoreList,
                          "exerciseLength": titleDict[i[1]]["exerciseLength"]}

            detailList.append(detailDict)
        end_time = time.time()

        print("阶段11耗时：", end_time - start_time)
        end_time = time.time()

        result["detailList"] = detailList
        result["id"]=int(classId)
        return JsonResponse({"code": 1, "status": 0, "data": result})


class ResetScore(View):
    def get(self, request):
        id = request.GET.get("id")
        reset_type = request.GET.get("reset_type")
        class_id = request.GET.get("class_id")
        group_id = request.GET.get("group_id")
        if reset_type == None:
            userScore = ClassUserExerciseInfo.objects.get(id=id)
            userScore.score = -1
            userScore.is_reset = 1
            userScore.save()
            UserExercise.objects.filter(user_id=userScore.user_id).filter(exercise_id=userScore.exercise_id).update(
                is_reset=1)
            ClassUserExerciseInfo.objects.filter(user_id=userScore.user_id).filter(
                exercise_id=userScore.exercise_id).update(is_reset=1, score=-1)
            classinfo = Classinfo.objects.filter(id=userScore.class_id).first()
            if classinfo is not None:
                cache.set("class_score_update_" + str(classinfo.class_id) + "_" + str(classinfo.teacherid), True, 10)

        #     该习题所有分数重置
        elif reset_type == "1":

            userScores = ClassUserExerciseInfo.objects.filter(exercise_id=id).filter(class_id=class_id).filter(
                group_id=group_id)
            for i in userScores:
                i.score = -1
                i.is_reset = 1
                i.save()
                UserExercise.objects.filter(user_id=i.user_id).filter(exercise_id=i.exercise_id).update(
                    is_reset=1)
            classinfo = Classinfo.objects.filter(id=class_id).first()
            if classinfo is not None:
                cache.set("class_score_update_" + str(class_id) + "_" + str(classinfo.teacherid), True, 10)
        elif reset_type == "2":
            userScores = ClassUserExerciseInfo.objects.filter(class_id=class_id).filter(
                group_id=group_id)
            for i in userScores:
                i.score = -1
                i.is_reset = 1
                i.save()
                UserExercise.objects.filter(user_id=i.user_id).filter(exercise_id=i.exercise_id).update(
                    is_reset=1)
            classinfo = Classinfo.objects.filter(id=class_id).first()
            if classinfo is not None:
                cache.set("class_score_update_" + str(class_id) + "_" + str(classinfo.teacherid), True, 10)

        return JsonResponse({"code": 1, "message": "重置成功"})


class AddRemark(View):
    def post(self, request):
        # 此处需要修改
        received_json_data = json.loads(request.body.decode())
        try:
            id = received_json_data["id"]
            content = received_json_data["content"]
        except Exception as e:
            message = "参数不全"
            return JsonResponse({"code": -2, "message": message})
        userScore = ClassUserExerciseInfo.objects.get(id=id)
        userScore.remark = content
        userScore.save()
        return JsonResponse({"code": 1, "message": "笔记添加成功"})


from adminApp.models import Config


class SetCopyScore(View):
    def get(self, request):
        authInfo = LoginAuth(request, (1, 2))
        if authInfo == False:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})
        id = request.GET.get("id")
        # 获取用户的copy次数
        userScore = ClassUserExerciseInfo.objects.get(id=id)
        if userScore.is_copy == 1:
            userScore.is_copy = 0
            userScore.copy_num = 0
            userScore.total_copy_num = 0

        userScore.save()
        return JsonResponse({"code": 1, "message": "设置抄写成功"})


class DelExerciseGroup(View):

    @transaction.atomic
    def get(self, request):
        authInfo = LoginAuth(request, (1, 2))
        if authInfo == False:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})

        id = request.GET.get("id")
        ExerciseRelationGroup.objects.filter(groupId=id).delete()
        ExerciseGroup.objects.get(id=id).delete()
        return JsonResponse({"code": 1})


class ExerciseGroupTitleList(View):
    def get(self, request):
        group = ExerciseGroup.objects.all().order_by("-id")
        result = []
        result_key = []
        for i in group:
            dict1 = {}
            dict1["key"] = i.id
            dict1["label"] = i.name
            dict1["desc"] = None
            result_key.append(i.id)
            result.append(dict1)

        return JsonResponse({"code": 1, "data": {"detail": result, "keys": result_key}})


import time


class UpdateStartTime(View):
    def get(self, request):
        problemId = request.GET.get("problemId")
        loginId = request.GET.get('loginId')
        try:
            user = cache.get(loginId)
            user_id, user_role = user.split("_")
        except:
            return JsonResponse({"code": -1, 'message': "该用户没有登录或者没有权限"})
        durationProblem = DurationProblem.objects.filter(user_id=user_id).filter(exercise_id=problemId).first()
        t = time.time()

        if durationProblem is not None:
            durationProblem.start_time = int(t)
            durationProblem.save()
        else:
            DurationProblem.objects.create(user_id=user_id, exercise_id=problemId, start_time=int(t))

        return JsonResponse({"code": 1, "message": "succeed"})


class TestCaseAdd(View):

    def post(self, request, pk=None):
        obj = request.FILES.get('file')
        info = b''
        for i in obj.chunks():
            info += i

        data = addTestCase(obj.name, info)
        try:
            test_case_id = data["id"]

            test_case_score = data["info"]
        except:
            return JsonResponse({"code": -1, "message": "上传文件不符合格式"})

        if pk != None and pk != "" and pk != "9999999999999":
            exercise = Exercise.objects.filter(pk=pk).first()
            if exercise.source_type == 3:
                try:
                    ProblemDetail.objects.filter(pk=pk).update(test_id=data["test_case_id"],
                                                               test_info=data["info"])
                except:
                    ProblemDetail.objects.filter(pk=pk).update(test_id=data["id"], test_info=str(data["info"])
                                            )

                problemDetail = ProblemDetail.objects.filter(pk=pk).first()
                sampleDetail = SampleDetail.objects.filter(problem_detail_id=pk)
                sampleList = []
                for i in sampleDetail:
                    dict1 = {"input": i.input, "output": i.output}
                    sampleList.append(dict1)
                result = addproblem(problemDetail.oj_id, pk, problemDetail.title, problemDetail.description,
                                    problemDetail.input_description, problemDetail.output_description,
                                    problemDetail.time_limit, problemDetail.memory_limit,
                                    sampleList,
                                    test_case_id, test_case_score, problemDetail.hint)
            else:
                desction = "本数据由爬虫提供"
                input_description = "本数据由爬虫提供"
                output_description = "本数据由爬虫提供"
                hint = "本数据由爬虫提供"
                sample = [{"input": "本数据由爬虫提供", "output": "本数据由爬虫提供"}]
                time_limit = 1200
                memory_limit = 256
                title = exercise.title
                # 如果是爬虫数据修改
                exercise = Exercise.objects.filter(pk=pk).first()
                # 标优字段进行标注
                exercise.not_good = 0
                caseScore = int(100 / len(test_case_score))
                for i in test_case_score:
                    i["score"] = caseScore
                # 没有添加过数据
                if exercise.can_test == 0:
                    # 添加数据进入爬虫中
                    result = addproblem(None, pk, title, desction, input_description, output_description, time_limit,
                                        memory_limit,
                                        sample,
                                        test_case_id, test_case_score, hint)
                    exercise.can_test = 1
                    problemDetail = ProblemDetail.objects.create(id=exercise.id, oj_id=result['id'], oj_id_0=pk,
                                                                 title=title, description=desction,
                                                                 input_description=input_description,
                                                                 output_description=output_description, hint=hint,
                                                                 time_limit=time_limit, memory_limit=memory_limit,
                                                                 test_id=test_case_id, test_info=test_case_score,
                                                                 content=exercise.content)
                    exercise.content = None
                    exercise.save()
                # 添加过数据
                else:
                    ProblemDetail.objects.filter(pk=pk).update(
                        test_id=test_case_id, test_info=test_case_score)
                    problemDetail = ProblemDetail.objects.filter(pk=pk).first()

                    addproblem(problemDetail.oj_id, pk, title, desction, input_description, output_description,
                               time_limit,
                               memory_limit,
                               sample,
                               test_case_id, test_case_score, hint)
        return JsonResponse({"code": 1, "message": "succeed", "data": data})
import uuid
import os
class UplodImage(View):
    def post(self,request):
        fileinfo = request.FILES.getlist("img"),
        info=fileinfo[0][0]

        name=str(uuid.uuid4())+"."+info.name.split(".")[-1]
        with open("./static/images/"+name,"wb") as f:
            for content in info.chunks():  # pic.chunks文件内容
                f.write(content)
        return JsonResponse({"url":"/api/static/images/"+name})

class                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   ExerciseAdd(APIView):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        try:
            title = data['title']
            title = parse.unquote(title)
        except:
            message = "参数不全"
            return JsonResponse({"code": -2, "message": message})

        desction = data["desction"]
        input_description = data["input_description"]
        output_description = data["output_description"]
        hint = data["hint"]
        sample = data["sample"]
        test_case_id = data["test_case_id"]
        test_case_score = data["test_case_score"]
        try:
            time_limit = data['time_limit']
            if time_limit == "":
                time_limit = 1200
        except:
            time_limit = 1200

        try:
            memory_limit = data['memory_limit']
            if memory_limit == "":
                memory_limit = 256
        except:
            memory_limit = "256"

        try:
            group_id = data['group_id']
        except:
            group_id = None

        try:
            order_after_exercise_id = data["order_desc"]
        except Exception as e:
            order_after_exercise_id = None
        print(order_after_exercise_id)

        caseScore = int(100 / len(test_case_score))
        for i in test_case_score:
            i["score"] = caseScore

        smaple2 = []
        for i in sample:
            if i["input"] == "" or i['output'] == "":
                continue
            smaple2.append(i)
        while True:
            oj_id = str(random.randint(100000, 1000000))
            problemDetail=ProblemDetail.objects.filter(oj_id_0=oj_id).first()
            if problemDetail is not None:
                continue
            else:
                break
        result = addproblem(None, oj_id, title, desction, input_description, output_description, time_limit,
                            memory_limit, smaple2,
                            test_case_id, test_case_score, hint)
        test_info = json.dumps(test_case_score)

        exercise = Exercise.objects.create(exerciseid=result["_id"], title=title,
                                           url="http://zuoye.0101jiaoyu.com:8081/problem/" + oj_id + "/", state=1,
                                           source_type=3, is_copy=0, can_test=1, not_good=0)
        problemDetail = ProblemDetail.objects.create(id=exercise.id, oj_id=result["id"], oj_id_0=oj_id, title=title,
                                                     description=desction,
                                                     input_description=input_description,
                                                     output_description=output_description, hint=hint,
                                                     time_limit=time_limit, memory_limit=memory_limit,
                                                     test_info=test_info, test_id=test_case_id)
        for i in smaple2:
            SampleDetail.objects.create(input=i['input'], output=i['output'], problem_detail_id=problemDetail.id)

        if group_id is not None :
            if  int(group_id) != 999999999:
                exerciseAfter = ExerciseRelationGroup.objects.filter(groupid=group_id).filter(
                    exerciseid=order_after_exercise_id).first()

            if int(order_after_exercise_id) == 999999999:
                addExerciseToUser(group_id, exercise.id, 0, 1)

            else:
                addExerciseToUser(group_id, exercise.id, exerciseAfter.ischallenge, exerciseAfter.orderdesc)
        else:
            addExerciseToUser(group_id, exercise.id, 0, 1)

        return JsonResponse({"code": 1, "message": "succeed"})


import json
import urllib.parse as parse


class ExerciseOption(APIView):
    def get(self, request, pk, format=None):
        try:
            exercise = Exercise.objects.get(pk=pk)
        except Exception as e:
            return Response({"code": -2, "message": "没有该数据"})

        loginId = request.GET.get("loginId")

        userid = cache.get(loginId)


        if userid is not None:
            user_id, state = userid.split("_")
            if str(state)!="2":
                return Response({"code": -2, "message": "没用权限"})

        else:
            return Response({"code": -2, "message": "没用权限"})
        data = {}
        data['title'] = exercise.title
        data['id'] = exercise.id
        if exercise.source_type == 3:
            problemDetail = ProblemDetail.objects.get(pk=pk)
            data["type"] = "self"
            data["desction"] = problemDetail.description
            data["title"] = problemDetail.title
            data["input_description"] = problemDetail.input_description
            data["output_description"] = problemDetail.output_description
            data["hint"] = problemDetail.hint
            samplelist2 = []
            samplelist = SampleDetail.objects.filter(problem_detail_id=pk)
            for i in samplelist:
                dict1 = {}
                dict1["input"] = i.input
                dict1["output"] = i.output
                samplelist2.append(dict1)
            data['sample'] = samplelist2

        else:
            data["type"] = "three"
            data['content'] = exercise.content
        return Response({"code": 1, "data": data})

    def post(self, request, pk):
        data = json.loads(request.body.decode("utf-8"))
        type2 = data["type"]
        try:
            title = data['title']
            title = parse.unquote(title)
        except Exception as e:
            print(e)
            message = "参数不全"

            return JsonResponse({"code": -2, "message": message})

        test_case_id = data["test_case_id"]

        test_case_score = data["test_case_score"]
        isRealNow = True
        if test_case_id is None:
            try:
                problemDetail = ProblemDetail.objects.filter(pk=pk).first()
                test_case_id = problemDetail.test_id
                test_case_score = problemDetail.test_info
                test_case_score = json.loads(test_case_score.replace("'", '"'))
            except Exception as e:
                print(e)
                isRealNow = False
            isAdd = False
        else:
            isAdd = True

        if str(type2) == "1":
            desction = data["desction"]
            input_description = data["input_description"]
            output_description = data["output_description"]
            hint = data["hint"]
            sample = data["sample"]
            try:
                time_limit = data['time_limit']
                isAdd = True

            except:
                time_limit = 1200

            try:
                memory_limit = data['memory_limit']
                isAdd = True

            except:
                memory_limit = 256
            Exercise.objects.filter(pk=pk).update(title=title)

            ProblemDetail.objects.filter(pk=pk).update(title=title, description=desction,
                                                       input_description=input_description,
                                                       output_description=output_description, hint=hint,
                                                       time_limit=time_limit, memory_limit=memory_limit,
                                                       test_id=test_case_id, test_info=test_case_score)

            SampleDetail.objects.filter(problem_detail_id=pk).delete()
            for i in sample:
                print(i)
                SampleDetail.objects.create(problem_detail_id=pk, input=i['input'], output=i['output'])
            problemDetail = ProblemDetail.objects.filter(pk=pk).first()

            result = addproblem(problemDetail.oj_id, pk, title, desction, input_description, output_description,
                                time_limit, memory_limit,
                                sample,
                                test_case_id, test_case_score, hint)
        else:

            try:
                content = data['desction']
            except:
                message = "参数不全"
                return JsonResponse({"code": -2, "message": message})
            Exercise.objects.filter(pk=pk).update(title=title, content=content)

            desction = "本数据由爬虫提供"
            input_description = "本数据由爬虫提供"
            output_description = "本数据由爬虫提供"
            hint = "本数据由爬虫提供"
            sample = [{"input": "本数据由爬虫提供", "output": "本数据由爬虫提供"}]
            time_limit = 1200
            memory_limit = 256

            # 如果是爬虫数据修改
            exercise = Exercise.objects.filter(pk=pk).first()
            if isRealNow == False:
                exercise.content = content
                exercise.title = title
                exercise.save()

            elif exercise.can_test == 0:

                if isAdd == False:
                    test_case_score = json.loads(test_case_score)
                else:
                    # 标优字段进行标注
                    exercise.not_good = 0

                caseScore = int(100 / len(test_case_score))
                for i in test_case_score:
                    i["score"] = caseScore

                # 添加数据进入爬虫中
                result = addproblem(None, pk, title, desction, input_description, output_description, time_limit,
                                    memory_limit,
                                    sample,
                                    test_case_id, test_case_score, hint)
                exercise.can_test = 1

                problemDetail = ProblemDetail.objects.create(id=exercise.id, oj_id=result['id'], oj_id_0=pk,
                                                             title=title, description=desction,
                                                             input_description=input_description,
                                                             output_description=output_description, hint=hint,
                                                             time_limit=time_limit, memory_limit=memory_limit,
                                                             test_id=test_case_id, test_info=test_case_score,
                                                             content=exercise.content)
                exercise.content = None
                exercise.save()
            else:

                if isAdd == False:
                    test_case_score = json.loads(test_case_score)

                caseScore = int(100 / len(test_case_score))
                for i in test_case_score:
                    i["score"] = caseScore

                ProblemDetail.objects.filter(pk=pk).update(title=title, description=desction,
                                                           input_description=input_description,
                                                           output_description=output_description, hint=hint,
                                                           time_limit=time_limit, memory_limit=memory_limit,
                                                           test_id=test_case_id, test_info=test_case_score)
                problemDetail = ProblemDetail.objects.filter(pk=pk).first()

                addproblem(problemDetail.oj_id, pk, title, desction, input_description, output_description, time_limit,
                           memory_limit,
                           sample,
                           test_case_id, test_case_score, hint)

        return JsonResponse({"code": 1, "message": "修改成功"})

    def delete(self, request, pk, format=None):
        Exercise.objects.filter(pk=pk).delete()
        problemDetail = ProblemDetail.objects.filter(pk=pk).first()
        SampleDetail.objects.filter(pk=pk).delete()
        if problemDetail is not None:
            delproblem(problemDetail.oj_id)
        ProblemDetail.objects.filter(pk=pk).delete()
        return JsonResponse({"code": 1, "message": "shanchu成功"})


class ExerciseGroupApi(APIView):
    def get(self, request):
        exerciseGroup = ExerciseGroup.objects.all()
        data = []
        data.append({"id": 999999999, "name": "不排序"})
        for i in exerciseGroup:
            dict1 = {}
            dict1["id"] = i.id
            dict1["name"] = i.name
            data.append(dict1)

        return JsonResponse({"code": 1, "message": "success", "data": data})


class ExerciseInGroup(APIView):
    def get(self, request, pk):
        data = []
        if int(pk) != 999999999:
            exerciseRelationGroup = ExerciseRelationGroup.objects.filter(groupid=pk)
            data.append({"id": 999999999, "name": "不排序"})
            for i in exerciseRelationGroup:
                exercise = Exercise.objects.get(id=i.exerciseid)
                dict1 = {}
                dict1["name"] = exercise.title
                dict1["id"] = i.exerciseid
                data.append(dict1)
        return JsonResponse({"code": 1, "message": "success", "data": data})


class CopyRankView(APIView):
    def get(self, request, class_id, exercise_id):
        if class_id != "all":
            ranklist = CopyRank.objects.filter(class_id=class_id).filter(exercise_id=exercise_id).order_by("-speed")
        else:
            ranklist = CopyRank.objects.filter(exercise_id=exercise_id).order_by("-speed")
        result = []
        for i in ranklist:
            dict1 = {}
            userinfo = UserInfo.objects.filter(id=i.user_id).first()
            if userinfo != None:
                dict1["speed"] = i.speed
                dict1["user"] = userinfo.username
                result.append(dict1)

        return JsonResponse({"code": 1, "message": "success", "data": result})


# 某一个学生习题，抄写次数显示
class CopyNumShowSingle(APIView):
    def get(self, request, pk):
        classuserExerciseInfo = ClassUserExerciseInfo.objects.filter(id=pk).first()

        total_copy_num = classuserExerciseInfo.total_copy_num
        if total_copy_num == 0:
            config = Config.objects.get(key="copy_num")
            total_copy_num = config.value
        return JsonResponse({"code": 1, "data": total_copy_num})

    def post(self, request, pk):
        data = json.loads(request.body.decode("utf-8"))
        num = data["num"]
        classuserExerciseInfo = ClassUserExerciseInfo.objects.get(id=pk)
        classuserExerciseInfo.total_copy_num = num
        classuserExerciseInfo.is_copy = 1
        classuserExerciseInfo.save()
        return JsonResponse({"code": 1})


class ResetScoreView(APIView):
    def get(self, request, datatype, class_id, pk):
        # 0更新习题组
        # 1更新班级
        if datatype == "0":
            userscore = ClassUserExerciseInfo.objects.filter(group_id=pk).filter(class_id=class_id)
            userscore.is_reset = 1
            userscore.score = -1
            userscore.save()
            exerciseGroupList = ExerciseRelationGroup.objects.filter(groupid=pk)
            for i in exerciseGroupList:
                userexercise = UserExercise.objects.filter(exercise_id=i.exerciseid)
                userexercise.is_reset = 1
                userexercise.save()
        elif datatype == "1":
            userscore = ClassUserExerciseInfo.objects.filter(exercise_id=pk).filter(class_id=class_id)
            userscore.is_reset = 1
            userscore.score = -1
            userscore.save()

            userexercise = UserExercise.objects.filter(exercise_id=pk)
            userexercise.is_reset = 1
            userexercise.save()

        cache.set("class_score_update_" + str(class_id), True, 10)
        return JsonResponse({"code": 1})


class UploadMainImage(View):
    def post(self, request, id):
        file = request.FILES.get("images")
        end = file.name.split(".")[-1]
        self.content = file.read()
        self.name = str(uuid.uuid4()) + "." + end
        if self.uploadVideo():
            url = "https://video-common.oss-cn-shenzhen.aliyuncs.com/" + self.name
            Exercise.objects.filter(id=id).update(answer_url=url)
            return JsonResponse({"code": 1, "message": "修改成功"})
        else:
            return JsonResponse({"code": -2, "message": "上传失败"})

    def uploadVideo(self):

        # 阿里云主账号AccessKey拥有所有API的访问权限，风险很高。强烈建议您创建并使用RAM账号进行API访问或日常运维，请登录 https://ram.console.aliyun.com 创建RAM账号。
        auth = oss2.Auth('LTAI4FzGLGU9yNsBVJPLBKNh', '1ehJc1LK2KiKtuJe1Y8pu62hQjspJw')
        # Endpoint以杭州为例，其它Region请按实际情况填写。
        bucket = oss2.Bucket(auth, 'http://oss-cn-shenzhen.aliyuncs.com', 'video-common')
        # http://video-common.oss-cn-shenzhen.aliyuncs.com
        result = bucket.put_object(self.name, self.content)

        # HTTP返回码。
        print('http status: {0}'.format(result.status))
        # 请求ID。请求ID是请求的唯一标识，强烈建议在程序日志中添加此参数。
        print('request_id: {0}'.format(result.request_id))
        # ETag是put_object方法返回值特有的属性。
        print('ETag: {0}'.format(result.etag))
        # HTTP响应头部。
        print('date: {0}'.format(result.headers['date']))
        if int(result.status) == 200:
            return True
        else:
            return False
