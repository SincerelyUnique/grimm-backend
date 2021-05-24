import json
from datetime import datetime, timedelta

from flask import request, jsonify

from grimm import logger, db
from grimm.activity import activity, activitybiz
from grimm.models.activity import Activity, RegisteredActivity, ActivityParticipant
from grimm.models.admin import User
from grimm.utils import dbutils, certificationgenerate, emailverify
from grimm.utils.constants import TAG_LIST


@activity.route("/activities", methods=['GET'])
def activities():
    keyword = request.args.get("keyword")
    activities_info = Activity.query.all()
    activities_info = [dbutils.serialize(rep) for rep in activities_info]
    if not activities_info: 
        return jsonify([])

    if keyword and len(keyword) != 0:
        queries = [activitybiz.activity_converter(activity)
                   for activity in activities_info if activity and keyword in activity["title"]]
        logger.info("get all activities successfully")
        return jsonify(queries)

    target_tag_list = request.args.get("tags")
    if not target_tag_list or len(target_tag_list) == 0:
        target_tag_list = "all"
    filter_time = request.args.get("time")
    if not filter_time or len(filter_time) == 0:
        filter_time = "all"
    sorted_activities_info = activitybiz.sort_by_time(activities_info, filter_time)
    queries = [activitybiz.activity_converter(activity)
               for activity in sorted_activities_info
               if activitybiz.should_append_by_tag(activity, target_tag_list)]
    logger.info("get all activities successfully")
    return jsonify(queries)


@activity.route("/activity", methods=["POST"])
def new_activity():
    """ view function to add new activity """
    info = json.loads(request.get_data())
    activity_info = Activity()
    logger.info('Add activity.')
    activity_info.approver = info["adminId"]
    activity_info.title = info["title"]
    activity_info.location = info["location"]
    activity_info.sign_in_radius = info["sign_in_radius"]
    activity_info.start_time = info["start_time"]
    activity_info.end_time = info["end_time"]
    activity_info.content = info["content"]
    activity_info.notice = info["notice"]
    activity_info.others = info["others"]
    activity_info.admin_raiser = info["adminId"]
    ids = ','.join([str(TAG_LIST.index(t)) for t in info["tag"].split(',') if t and t in TAG_LIST]) if info["tag"] else ''
    activity_info.tag_ids = ids
    activity_info.volunteer_capacity = info["volunteer_capacity"]
    activity_info.vision_impaired_capacity = info["vision_impaired_capacity"]
    activity_info.volunteer_job_title = info["volunteer_job_title"]
    activity_info.volunteer_job_content = info["volunteer_job_content"]
    activity_info.activity_fee = info["activity_fee"] if 'activity_fee' in info else 0
    db.session.add(activity_info)
    db.session.commit()
    logger.info("%s: create new activity successfully", activity_info.title)
    return jsonify({"status": "success"})


@activity.route("/activity/<int:activity_id>", methods=["POST", "GET", "DELETE"])
def activity_(activity_id):
    if request.method == 'GET':
        activity = Activity.query.filter(Activity.id == activity_id).first()
        if not activity:
            logger.warning("%d: no such activity", activity_id)
            return jsonify({"status": "failure", "message": "未知活动ID"})
        feedback = activitybiz.activity_converter(dbutils.serialize(activity))
        logger.info("%d: get activity successfully", activity_id)
        return jsonify(feedback)
    if request.method == 'POST':
        newinfo = json.loads(request.get_data())
        activity_info = db.session.query(Activity).filter(Activity.id == activity_id).first()
        if not activity_info:
            logger.warning("%d: update activity failed", activity_id)
            feedback = {"status": "failure", "message": "无效活动 ID"}
            return jsonify(feedback)
        logger.info('Will add activity.')
        activity_info.approver = newinfo["adminId"]
        activity_info.title = newinfo["title"]
        activity_info.location = newinfo["location"]
        activity_info.sign_in_radius = newinfo["sign_in_radius"]
        activity_info.start_time = newinfo["start_time"]
        activity_info.end_time = newinfo["end_time"]
        activity_info.content = newinfo["content"]
        activity_info.notice = newinfo["notice"]
        activity_info.others = newinfo["others"]
        activity_info.admin_raiser = newinfo["adminId"]
        ids = ','.join([str(TAG_LIST.index(t)) for t in newinfo["tag"].split(',') if t and t in TAG_LIST]) if newinfo["tag"] else ''
        activity_info.tag_ids = ids
        activity_info.volunteer_capacity = newinfo["volunteer_capacity"]
        activity_info.vision_impaired_capacity = newinfo["vision_impaired_capacity"]
        activity_info.volunteer_job_title = newinfo["volunteer_job_title"]
        activity_info.volunteer_job_content = newinfo["volunteer_job_content"]
        activity_info.activity_fee = newinfo["activity_fee"]
        db.session.commit()
        logger.info("%d: update activity successfully", activity_id)
        return jsonify({"status": "success"})
    if request.method == 'DELETE':
        activity = Activity.query.filter(Activity.id == activity_id).first()
        db.session.delete(activity)
        db.session.commit()
        logger.info("%d: delete new activity successfully", activity_id)
        return jsonify({"status": "success"})


@activity.route("/activityRegistration/<int:activity_id>", methods=["POST", "GET"])
def activity_registration(activity_id):
    if request.method == 'GET':
        activity_info = Activity.query.filter(Activity.id == activity_id).first()
        if not activity_info:
            logger.warning("%d: no such activity", activity_id)
            return jsonify({"status": "failure", "message": "无效活动 ID"})
        activities_registration = RegisteredActivity.query.filter(RegisteredActivity.activity_id == activity_id).all()
        users = []
        for item in activities_registration:
            user = {}
            openid = item.user_openid
            user_info = User.query.filter(User.openid == openid).first()
            user["openid"] = openid
            user["name"] = user_info.name
            user["role"] = user_info.role
            user["phone"] = item.phone
            user["address"] = item.address
            user["accepted"] = item.accepted
            user["needpickup"] = item.needpickup
            user["topickup"] = item.topickup
            users.append(user)
        feedback = {'status': 'success', 'users': users}
        return jsonify(feedback)
    if request.method == 'POST':
        activity_info = Activity.query.filter(Activity.id == activity_id).first()
        if not activity_info:
            return jsonify({"status": "failure", "message": "无效活动 ID"})
        openid = request.args.get("openid")
        accepted = request.args.get("accepted")
        activities_registration = RegisteredActivity.query.\
            filter(RegisteredActivity.activity_id == activity_id, RegisteredActivity.user_openid == openid).all()
        if not activities_registration:
            return jsonify({"status": "failure", "message": " 此人未报名"})
        num_rows_updated = RegisteredActivity.query.\
            filter(RegisteredActivity.activity_id == activity_id,
                   RegisteredActivity.user_openid == openid).update({RegisteredActivity.accepted: accepted})
        logger.info('%s rows updated.' % num_rows_updated)
        db.session.commit()
        return jsonify({"status": "success"})


@activity.route("/activityParticipant", methods=["GET", 'POST'])
def activity_participant():
    if request.method == 'GET':
        participant_openid = request.args.get("participant_openid")
        activity_participant_infos = ActivityParticipant.query.all()
        logger.info("query all activity_participant info successfully")
        feedback = {"status": "success", "participant_openid": participant_openid, "activities": []}
        for activity_participant in activity_participant_infos:
            if activity_participant["participant_openid"] == participant_openid:
                activity_id = int(activity_participant["activity_id"])
                activity_info = Activity.query.filter(Activity.id == activity_id).first()
                activity = {"id": activity_info["id"], "title": activity_info["title"],
                            "location": activity_info["location"]}
                start = activity_info["start_time"]
                end = activity_info["end_time"]
                activity["start_time"] = start.strftime("%Y-%m-%dT%H:%M:%S")
                activity["end_time"] = end.strftime("%Y-%m-%dT%H:%M:%S")
                activity["content"] = activity_info["content"]
                activity["certificated"] = activity_participant["certificated"]
                feedback["activities"].append(activity)
                # email_verify.send("email_resource/confirm-user.html",
                # "jftt_pt@hotmail.com", "test", "test", "12345678")
        return jsonify(feedback)
    if request.method == 'POST':
        info = request.get_json()
        participant_openid = info.get("participant_openid", None)
        activity_id = info.get("activity_id", None)
        real_name = info.get("real_name", None)
        id_type = info.get("id_type", None)
        idcard = info.get("idcard", None)
        email = info.get("email", None)
        paper_certificate = info.get("paper_certificate", None)
        activity_info = Activity.query.filter(Activity.id == activity_id).first()
        activity_title = activity_info.get("title", None)
        start = activity_info["start_time"]
        end = activity_info["end_time"]
        activity_duration = (end - start).days * 24 + (end - start).seconds // 3600
        feedback = {"status": "success",
                    "participant_openid": participant_openid,
                    "activity_id": activity_id,
                    "activity_title": activity_title,
                    "real_name": real_name,
                    "id_type": id_type,
                    "idcard": idcard,
                    "email": email,
                    "paper_certificate": paper_certificate}
        ActivityParticipant.query.\
            filter(ActivityParticipant.participant_openid == participant_openid,
                   ActivityParticipant.activity_id == activity_id).\
            update({ActivityParticipant.certificated: 0})
        activity_participant_info = db.session.query(ActivityParticipant).\
            filter(ActivityParticipant.activity_id == activity_id,
                   ActivityParticipant.participant_openid == participant_openid).first()
        logger.info(activity_participant_info)

        certificated_user_info = db.session.query.filter(User.openid == participant_openid).first()
        certificated_user_info.real_name = real_name
        certificated_user_info.id_type = id_type
        certificated_user_info.idcard = idcard
        certificated_user_info.email = email

        certificated_info = {"paper_certificate": paper_certificate}
        if paper_certificate:
            recipient_name = info.get("recipient_name", None)
            recipient_address = info.get("recipient_address", None)
            recipient_phone = info.get("recipient_phone", None)
            certificated_user_info.recipient_name = recipient_name
            certificated_user_info.recipient_address = recipient_address
            certificated_user_info.recipient_phone = recipient_phone
            feedback["recipient_name"] = recipient_name
            feedback["recipient_address"] = recipient_address
            feedback["recipient_phone"] = recipient_phone
        if not activity_participant_info.certificated:
            certificated_info["certificated"] = 1
            certificated_info["certificate_date"] = datetime.now().strftime("%Y-%m-%d")
            activity_participant_info.paper_certificate = paper_certificate
            activity_participant_info.certificated = 1
            activity_participant_info.certificate_date = 1

            # update participant's related user info in user table
            logger.info(dbutils.serialize(certificated_user_info))
            db.session.commit()

            certification_info = {"name": real_name,
                                  "certificate_type": id_type,
                                  "certificate_code": idcard,
                                  "activity_title": activity_title,
                                  "activity_during": str(activity_duration) + "小时",
                                  "director": "王臻",
                                  "manager": "刘莉娟",
                                  "contact_code": "1388888888"}

            certification_file = certificationgenerate.generate_certification(certification_info)

            emailverify.send("email_resource/certificate-letter.html",
                              email, real_name + "'s certification",
                              "test", "12345678",
                              attachment_file=certification_file)

        return jsonify(feedback)


@activity.route("/myActivities", methods=["GET"])
def get_favorite_activities():
    openid = request.headers.get("Authorization")
    target_filter = request.args.get("filter")
    if not target_filter or len(target_filter) == 0:
        target_filter = "all"

    favorite_activities_info = db.session.query(Activity.id, Activity.end_time). \
        filter(ActivityParticipant.participant_openid == openid). \
        filter(ActivityParticipant.interested == 1). \
        filter(ActivityParticipant.activity_id == Activity.id).all()
    registered_activities_info = db.session.query(Activity.id, Activity.end_time). \
        filter(RegisteredActivity.user_openid == openid). \
        filter(RegisteredActivity.activity_id == Activity.id).all()
    favorite_activities_info = [{'activity.id': i.id, 'activity.end_time': i.end_time}
                                for i in favorite_activities_info] if favorite_activities_info else []
    registered_activities_info = [{'activity.id': j.id, 'activity.end_time': j.end_time}
                                  for j in registered_activities_info] if registered_activities_info else []

    target_activities_info = []
    if target_filter == "favorite":
        if favorite_activities_info is not None:
            for item in favorite_activities_info:
                target_activities_info.append(item)
    elif target_filter == "registered":
        if registered_activities_info is not None:
            for item in registered_activities_info:
                target_activities_info.append(item)
    elif target_filter == "all":
        id_set = []
        if favorite_activities_info is not None:
            for item in favorite_activities_info:
                target_activities_info.append(item)
                id_set.append(item["activity.id"])
        if registered_activities_info is not None:
            for item in registered_activities_info:
                if item["activity.id"] not in id_set:
                    target_activities_info.append(item)
                    id_set.append(item["activity.id"])
    target_activities_info.sort(
        key=lambda item: item["activity.id"], reverse=True
    )
    target_activities_info = [
        item
        for item in target_activities_info
        if datetime.today() - timedelta(days=365) < item["activity.end_time"]
    ]

    queries = []
    for item in target_activities_info:
        activity_id = item["activity.id"]
        activity = Activity.query.filter(Activity.id == activity_id).first()
        activity = dbutils.serialize(activity)
        queries.append(activitybiz.activity_converter(activity, openid))
    return jsonify(queries)


@activity.route("/activity_detail", methods=["GET"])
def get_activity():
    """ get activity detail with activityId """
    openid = request.headers.get("Authorization")
    activity_id = int(request.args.get("activityId"))
    activity_info = Activity.query.filter(Activity.id == activity_id).first()
    if not activity_info:
        logger.warning("%d: no such activity", activity_id)
        return jsonify({"status": "failure", "message": "未知活动ID"})
    feedback = activitybiz.activity_converter(dbutils.serialize(activity_info), openid)
    feedback["status"] = "success"
    logger.info("%d: get activity successfully", activity_id)
    return jsonify(feedback)


@activity.route("/activity_detail/interest", methods=["POST"])
def mark_activity():
    """ mark activity as Interest """
    openid = request.headers.get("Authorization")
    activity_id = request.args.get("activityId")
    interest = request.args.get("interest")
    feedback = {"status": "success"}
    activity_participant_info = db.session.query(ActivityParticipant).\
        filter(ActivityParticipant.activity_id == activity_id,
               ActivityParticipant.participant_openid == openid).all()
    if activity_participant_info:
        ActivityParticipant.query.\
            filter(ActivityParticipant.activity_id == activity_id,
                   ActivityParticipant.participant_openid == openid).\
            update({ActivityParticipant.interested: interest})
        return jsonify(feedback)
    else:
        activity_participant_info = ActivityParticipant()
        activity_participant_info.activity_id = activity_id
        activity_participant_info.participant_openid = openid
        activity_participant_info.interested = interest
        activity_participant_info.share = 0
        activity_participant_info.thumbs_up = 0
        db.session.add(activity_participant_info)
        db.session.commit()
        logger.info("Create new activity_participant_info successfully")
        return jsonify(feedback)


@activity.route("/activity_detail/thumbs_up", methods=["POST"])
def thumbs_up_activity():
    """mark activity as thumbs_up"""
    openid = request.headers.get("Authorization")
    activity_id = request.args.get("activityId")
    thumbs_up = request.args.get("thumbs_up")
    feedback = {"status": "success"}
    activity_participant_info = db.session.query(ActivityParticipant). \
        filter(ActivityParticipant.activity_id == activity_id,
               ActivityParticipant.participant_openid == openid).all()
    if activity_participant_info:
        ActivityParticipant.query. \
            filter(ActivityParticipant.activity_id == activity_id,
                   ActivityParticipant.participant_openid == openid). \
            update({ActivityParticipant.thumbs_up: thumbs_up})
        return jsonify(feedback)
    else:
        activity_participant_info = ActivityParticipant()
        activity_participant_info.activity_id = activity_id
        activity_participant_info.participant_openid = openid
        activity_participant_info.interested = 0
        activity_participant_info.share = 0
        activity_participant_info.thumbs_up = thumbs_up
        db.session.add(activity_participant_info)
        db.session.commit()
        logger.info("Create new activity_participant_info successfully")
        return jsonify(feedback)


@activity.route("/activity_detail/share", methods=["POST"])
def share_activity():
    """ share activity """
    openid = request.headers.get("Authorization")
    activity_id = request.args.get("activityId")
    participant = db.session.query(ActivityParticipant). \
        filter(ActivityParticipant.activity_id == activity_id,
               ActivityParticipant.participant_openid == openid).all()
    if not participant:
        activity_participant_info = ActivityParticipant()
        activity_participant_info.activity_id = activity_id
        activity_participant_info.participant_openid = openid
        activity_participant_info.interested = 0
        activity_participant_info.share = 1
        activity_participant_info.thumbs_up = 0
        db.session.add(activity_participant_info)
        db.session.commit()
        logger.info("Create new activity_participant_info with share successfully")
        return jsonify({"status": "success"})

    participant = db.session.query(ActivityParticipant). \
        filter(ActivityParticipant.activity_id == activity_id,
               ActivityParticipant.participant_openid == openid).first()
    if not participant:
        logger.warning("%d: no such activity", activity_id)
        return jsonify({"status": "failure"})

    share_count = int(participant.share)
    share_count += 1
    ActivityParticipant.query. \
        filter(ActivityParticipant.activity_id == activity_id,
               ActivityParticipant.participant_openid == openid). \
        update({ActivityParticipant.share: share_count})
    return jsonify({"status": "success"})


@activity.route("/registeredActivities", methods=["POST", 'DELETE'])
def registered_activities():
    if request.method == 'POST':
        # register an activity
        openid = request.headers.get("Authorization")
        info = request.get_json()
        activity_id = info["activityId"]

        exist_info = RegisteredActivity.query.\
            filter(RegisteredActivity.user_openid == openid,
                   RegisteredActivity.activity_id == activity_id).first()
        if exist_info:
            return jsonify({"status": "failure", "message": "重复报名"})

        registerAct = RegisteredActivity()
        if "needPickUp" in info.keys():
            registerAct.needpickup = int(info["needPickUp"])
        if "toPickUp" in info.keys():
            registerAct.topickup = int(info["toPickUp"])
        if "phone" in info.keys():
            registerAct.phone = info["phone"]
        else:
            try:
                userinfo = User.query.filter(User.openid == openid).first()
                registerAct.phone = userinfo["phone"]
            except:
                return jsonify({"status": "failure", "message": "未能获取用户信息"})
        if "address" in info.keys():
            registerAct.address = info["address"]
        else:
            try:
                userinfo = User.query.filter(User.openid == openid).first()
                registerAct.address = userinfo.address
            except:
                return jsonify({"status": "failure", "message": "未能获取用户信息"})
        registerAct.user_openid = openid
        # activity_id from network is str
        registerAct.activity_id = int(activity_id)
        registerAct.accepted = -1

        # Auto approve, not auto reject -- Hangzhou Backend
        try:
            activeinfo = RegisteredActivity.query.filter(RegisteredActivity.activity_id == int(activity_id)).all()
            volunteer = db.session.query(ActivityParticipant.activity_id, User.openid).\
                filter(ActivityParticipant.activity_id == activity_id).\
                filter(ActivityParticipant.participant_openid == User.openid).\
                filter(User.role == 0).all()
            logger.error("%s: volunteer", volunteer)
            if activeinfo:
                logger.error("%s: activeinfo", activeinfo[0])
                if len(volunteer) < activeinfo[0]["volunteer_capacity"]:
                    registerAct.accepted = 1
            else:
                registerAct.accepted = -1
        except:
            logger.error("%s: activeinfo no return. Skip to auto approve, insert register still",)
            #return json_dump_http_response(
            #    {"status": "failure", "message": "未能获取志愿者人数信息"}
            #)

        db.session.add(registerAct)
        db.session.commit()
        return jsonify({"status": "success"})
    if request.method == 'DELETE':
        """ cancel specific registered activity """
        openid = request.headers.get("Authorization")
        print("*****************deleteopenid", type(openid), openid)
        activity_id = request.args.get("activityId")
        delete_info = db.session.query(RegisteredActivity).\
            filter(RegisteredActivity.user_openid == openid,
                   RegisteredActivity.activity_id == activity_id).first()
        if delete_info:
            db.session.delete(delete_info)
            db.session.commit()
            return jsonify({"status": "取消活动成功！"})
        return jsonify({"status": "取消活动失败！"})
