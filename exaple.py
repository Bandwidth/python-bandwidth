# from client import Client
#
#
#
# client = Client('useid', ('admin', 'admin'))
#
# client.calls.filter(to='+1213323234')
# # returns list of dictionaries
# # [Call(call_id='foo_bar')]
#
# client.calls.all()
# # returns of lazy iterator, first 100 will upload immediately, other will be uploaded on need
#
#
# c = client.create_call({'from': '+112321312', 'to': '+123435454665'})
#
# # c = Call for call id=foo
#
#
# class Call():
#     def __init__(self, client, *kwargs):
#         self.kwargs = kwargs
#
#
#
#
#
# # state intiall
#
#
# {
#    eventType: answer, callid: fooo
#
# }
#
# pikle(Call())
#
#
#
# c = client.Call(**answer)
#
# c.update_info_from_callback(callback_json)
#
# bridge = client.create_bridge({}, {})
# bridge.play_audio('dsadsad')
#
#
# # c = call.play_audio(
# c.events -> dict
#
#
# client.calls.filter(call_id='adsdsada')
#

import pickle
from client import Client


client = Client('foo', ())

call = client.Call('callinfo')

# callinfo

print(vars(call))


pk = pickle.dumps(call)

print(pk)

# call info loaded

np = pickle.loads(pk)
np.sent_dtmf()

print(vars(np))

