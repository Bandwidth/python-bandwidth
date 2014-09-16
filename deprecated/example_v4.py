from bandwith_sdk.client_v4 import Call, Bridge, Client

Client('u-**********', 't-******', 's-********')


print(Call.list())

the_call = Call.create('+14089155654', '+14088833839')


the_call.hangup()
the_call.call_id
the_call.start_time
the_call.active_time

print(the_call)
print(Call.get('c-p6eyxrjbsmi6zuef3t6zdpa'))
print(Call.get(the_call.call_id))
the_call.refresh()


Call('c-p6eyxrjbsmi6zuef3t6zdpa').send_dtmf('1')

Call('c-p6eyxrjbsmi6zuef3t6zdpa').play_audio('Hello.mp3')  # returns Call('c-p6eyxrjbsmi6zuef3t6zdpa')

# part of event
Call({"id": "c-zzzzzzzz",
     "direction": "out",
     "from": "+14089155654",
     "to": "+14088833839"}).play_audio(fileUrl='Hello.mp3')


the_call = Call.create('+14089155654', '+14088833839')

another_call = Call.create('+14089155654', '+14088833839')

#
bridge = the_call.bridge(another_call)
# or
bridge = Bridge.create(the_call, another_call)

bridge.play_audio('Hello.mp3')
bridge.stop_audio()


# empty bridge
bridge = Bridge.create()
# call and bridge
bridge.call('+14089155654', '+14088833839')
bridge.add_call(another_call)


print(bridge.call_ids)
print(bridge.calls)
print(bridge.fetch_calls())


# Serialization part

call = Call('dfdfdfdfdf')

import pickle
d = pickle.dumps(call)
print(d)
# b'\x80\x03cbandwith_sdk.client_v4\nCall\nq\x00)\x81q\x01X\n\x00\x00\x00dfdfdfdfdfq\x02b.' 89 bytes
r = pickle.loads(d)
print(r)
#Call(dfdfdfdfdf)
