
from sanic import response, Blueprint
from sanic_openapi import doc
from little_boxes.key import Key

from pubgate.db.models import User


user_v1 = Blueprint('user_v1', url_prefix='/api/v1/user')


@user_v1.route('/', methods=['POST'])
@doc.summary("Creates a user")
@doc.consumes(User, location="body")
async def create_user(request):
    if request.app.config.OPEN_REGISTRATION:
        username = request.json["username"]
        if username:
            is_uniq = await User.is_unique(doc=dict(username=username))
            if is_uniq in (True, None):
                await User.insert_one(dict(username=username,
                                           password=request.json["password"],
                                           email=request.json["email"]))
                return response.json({'peremoga': 'yep'})
            else:
                return response.json({'zrada': 'username n/a'})
    return response.json({'zrada': 'nope'})


@user_v1.route('/<user_id>', methods=['GET'])
@doc.summary("Returns user details")
async def get_user(request, user_id):
    user = await User.find_one(dict(username=user_id))
    if not user:
        return response.json({"error": "no such user"}, status=404)

    domain = request.app.config.DOMAIN
    key = Key(f"https://{domain}/user/{user_id}")
    key.new()
    return response.json(
        {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/v1",
                {
                    "manuallyApprovesFollowers": "as:manuallyApprovesFollowers",
                    "sensitive": "as:sensitive",
                    "movedTo": "as:movedTo",
                    "Hashtag": "as:Hashtag",
                    "ostatus": "http://ostatus.org#",
                    "atomUri": "ostatus:atomUri",
                    "inReplyToAtomUri": "ostatus:inReplyToAtomUri",
                    "conversation": "ostatus:conversation",
                    "toot": "http://joinmastodon.org/ns#",
                    "Emoji": "toot:Emoji",
                    "focalPoint": {
                        "@container": "@list",
                        "@id": "toot:focalPoint"
                    },
                    "featured": "toot:featured",
                    "schema": "http://schema.org#",
                    "PropertyValue": "schema:PropertyValue",
                    "value": "schema:value"
                }
            ],
            "id": f"https://{domain}/user/{user_id}",
            "type": "Person",
            "following": f"https://{domain}/outbox/{user_id}/following",
            "followers": f"https://{domain}/outbox/{user_id}/followers",
            "inbox": f"https://{domain}/inbox/{user_id}/inbox",
            "outbox": f"https://{domain}/outbox/{user_id}/outbox",
            "preferredUsername": f"{user_id}",
            "name": "",
            "summary": "<p></p>",
            "url": f"https://{domain}/@{user_id}",
            "manuallyApprovesFollowers": False,
            "publicKey": key.to_dict(),
            "tag": [],
            "attachment": [],
            "endpoints": {
                "sharedInbox": f"https://{domain}/inbox"
            },
            "icon": {
                "type": "Image",
                "mediaType": "image/png",
                "url": "https://d1nhio0ox7pgb.cloudfront.net/_img/g_collection_png/standard/512x512/torii.png"
            }
        }, headers={'Content-Type': 'application/jrd+json; charset=utf-8'}
    )
