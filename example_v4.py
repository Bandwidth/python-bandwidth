from bandwith_sdk.client_v4 import Call


print(Call.list())

the_call = Call.create('+14089155654', '+14088833839')


print(the_call.hangup())
the_call.call_id
the_call.start_time
the_call.active_time

print(the_call)
print(Call.get('c-p6eyxrjbsmi6zuef3t6zdpa'))
print(Call.get(the_call.call_id))
the_call.refresh()


Call('c-p6eyxrjbsmi6zuef3t6zdpa').send_dtmf('1')

Call('c-p6eyxrjbsmi6zuef3t6zdpa').play_audio(fileUrl='Hello.mp3')  # returns Call('c-p6eyxrjbsmi6zuef3t6zdpa')

# part of event
Call({"id": "c-zzzzzzzz",
     "direction": "out",
     "from": "+14089155654",
     "to": "+14088833839"}).play_audio(fileUrl='Hello.mp3')
