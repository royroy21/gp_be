# Chat

## New direct chat logic
- A user initiates a chat by posting to the `ws/chat/new/` URL
  (the room is specified as `new` not Room id as for an existing Chat). 
  A `JWT` should be sent along with a `type` of `direct` and the id of the user should be specified in 
  `to_user_id`. For example `ws/chat/?token=secret&type=direct&to_user_id=99`
- A Room entry in the database is created. The initiating user and the user specified in
  `to_user_id` are added to the members of Room.
- The room name is sent back to the client. Future messages are then posted to this room.
  For example `ws/chat/99/?token=secret`. 
  At this stage sending the `type` and `to_user_id` is not necessary.

## New chat in response to a gig logic
- A user initiates a chat by posting to the `ws/chat/new/` URL
  (the room is specified as `new` not Room id as for an existing Chat). 
  A `JWT` should be sent along with a `type` of `gig` and the id of the gig should be specified in
  `gig_id`. For example `ws/chat/?token=secret&type=gig&gig=99`
- A Room entry in the database is created. The initiating user and the user's Gig it is 
  (specified in `gig_id`) are added to the members of Room.
- A Chat entry in the database is created, the id of which is used as the room name. The room name is sent
  back to the user. Future messages are then posted to this room. 
  For example `ws/chat/99/?token=secret`. At this stage sending the `type` and `gig_id` is not necessary.

## Getting older messages for a room
- Use the URL `/api/chat/?room=99` should be used the first time a client connects so to get older messages
  for a room. If the client's user is not a member of the room a 403 error will be raised.
