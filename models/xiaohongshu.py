from typing import Dict, List

from tortoise import fields
from tortoise.models import Model

import config
from tools import utils


class XhsBaseModel(Model):
    id = fields.IntField(pk=True, autoincrement=True, description="自增ID")
    user_id = fields.CharField(max_length=64, description="用户ID")
    nickname = fields.CharField(null=True, max_length=64, description="用户昵称")
    avatar = fields.CharField(null=True, max_length=255, description="用户头像地址")
    ip_location = fields.CharField(null=True, max_length=255, description="评论时的IP地址")
    add_ts = fields.BigIntField(description="记录添加时间戳")
    last_modify_ts = fields.BigIntField(description="记录最后修改时间戳")

    class Meta:
        abstract = True


class XHSNote(XhsBaseModel):
    note_id = fields.CharField(max_length=64, index=True, description="笔记ID")
    type = fields.CharField(null=True, max_length=16, description="笔记类型(normal | video)")
    title = fields.CharField(null=True, max_length=255, description="笔记标题")
    desc = fields.TextField(null=True, description="笔记描述")
    time = fields.BigIntField(description="笔记发布时间戳", index=True)
    last_update_time = fields.BigIntField(description="笔记最后更新时间戳")
    liked_count = fields.CharField(null=True, max_length=16, description="笔记点赞数")
    collected_count = fields.CharField(null=True, max_length=16, description="笔记收藏数")
    comment_count = fields.CharField(null=True, max_length=16, description="笔记评论数")
    share_count = fields.CharField(null=True, max_length=16, description="笔记分享数")
    image_list = fields.TextField(null=True, description="笔记封面图片列表")

    class Meta:
        table = "xhs_note"
        table_description = "小红书笔记"

    def __str__(self):
        return f"{self.note_id} - {self.title}"


class XHSNoteComment(XhsBaseModel):
    comment_id = fields.CharField(max_length=64, index=True, description="评论ID")
    create_time = fields.BigIntField(index=True, description="评论时间戳")
    note_id = fields.CharField(max_length=64, description="笔记ID")
    content = fields.TextField(description="评论内容")
    sub_comment_count = fields.IntField(description="子评论数量")

    class Meta:
        table = "xhs_note_comment"
        table_description = "小红书笔记评论"

    def __str__(self):
        return f"{self.comment_id} - {self.content}"


async def update_xhs_note(note_item: Dict):
    note_id = note_item.get("note_id")
    user_info = note_item.get("user", {})
    interact_info = note_item.get("interact_info", {})
    image_list: List[Dict] = note_item.get("image_list", [])

    local_db_item = {
        "note_id": note_item.get("note_id"),
        "type": note_item.get("type"),
        "title": note_item.get("title") or note_item.get("desc", "")[:255],
        "desc": note_item.get("desc", ""),
        "time": note_item.get("time"),
        "last_update_time": note_item.get("last_update_time", 0),
        "user_id": user_info.get("user_id"),
        "nickname": user_info.get("nickname"),
        "avatar": user_info.get("avatar"),
        "liked_count": interact_info.get("liked_count"),
        "collected_count": interact_info.get("collected_count"),
        "comment_count": interact_info.get("comment_count"),
        "share_count": interact_info.get("share_count"),
        "ip_location": note_item.get("ip_location", ""),
        "image_list": ','.join([img.get('url', '') for img in image_list]),
        "last_modify_ts": utils.get_current_timestamp(),
    }
    print("xhs note:", local_db_item)
    if config.IS_SAVED_DATABASED:
        if not await XHSNote.filter(note_id=note_id).first():
            local_db_item["add_ts"] = utils.get_current_timestamp()
            await XHSNote.create(**local_db_item)
        else:
            await XHSNote.filter(note_id=note_id).update(**local_db_item)


async def update_xhs_note_comment(note_id: str, comment_item: Dict):
    user_info = comment_item.get("user_info", {})
    comment_id = comment_item.get("id")
    local_db_item = {
        "comment_id": comment_id,
        "create_time": comment_item.get("create_time"),
        "ip_location": comment_item.get("ip_location"),
        "note_id": note_id,
        "content": comment_item.get("content"),
        "user_id": user_info.get("user_id"),
        "nickname": user_info.get("nickname"),
        "avatar": user_info.get("image"),
        "sub_comment_count": comment_item.get("sub_comment_count"),
        "last_modify_ts": utils.get_current_timestamp(),
    }
    print("xhs note comment:", local_db_item)
    if config.IS_SAVED_DATABASED:
        if not await XHSNoteComment.filter(comment_id=comment_id).first():
            local_db_item["add_ts"] = utils.get_current_timestamp()
            await XHSNoteComment.create(**local_db_item)
        else:
            await XHSNoteComment.filter(comment_id=comment_id).update(**local_db_item)
