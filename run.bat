# python mainIAQPconsole.py -occupancy "Classrooms (age 9 plus)" -area_ft2 950   -Recirc_CFM 50
# python mainIAQPconsole.py -occupancy "Classrooms (age 9 plus)" -area_ft2 950   -Recirc_CFM 250
# python mainIAQPconsole.py -occupancy "Classrooms (age 9 plus)" -area_ft2 950   -Recirc_CFM 500



# 1 Dressing → Break rooms (General)
python mainIAQPconsole.py -occupancy "Break rooms (General)" -area_ft2 472 -num_people 12 -Recirc_CFM 50

# 2 Lobby-O → Lobbies
python mainIAQPconsole.py -occupancy "Lobbies"               -area_ft2 878 -num_people 29 -Recirc_CFM 50
python mainIAQPconsole.py -occupancy "Lobbies"               -area_ft2 205 -num_people  7 -Recirc_CFM 50

# 3 Office → Office space
python mainIAQPconsole.py -occupancy "Office space"          -area_ft2  78 -num_people  1 -Recirc_CFM 50
python mainIAQPconsole.py -occupancy "Office space"          -area_ft2 209 -num_people  2 -Recirc_CFM 50
python mainIAQPconsole.py -occupancy "Office space"          -area_ft2 204 -num_people  2 -Recirc_CFM 50
python mainIAQPconsole.py -occupancy "Office space"          -area_ft2 207 -num_people  2 -Recirc_CFM 50

# 4 Breakroom-G → Break rooms (General)
python mainIAQPconsole.py -occupancy "Break rooms (General)" -area_ft2 102 -num_people  3 -Recirc_CFM 50

# 5 ConferenceRm → Conference/meeting
python mainIAQPconsole.py -occupancy "Conference/meeting"    -area_ft2 231 -num_people 12 -Recirc_CFM 50
