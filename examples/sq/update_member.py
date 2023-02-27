from CHRLINE import CHRLINE

# default device CHROMEOS not support OpenChat.
cl = CHRLINE(device="IOSIPAD")

# ====================
UPDATE_TYPE = -1
UPDATE_ATTRS = []
UPDATE_PREF_ATTRS = []
MEMBER_MID = "pxxxxxxxxxxxx"  # Change this
SQUAER_MID = "sxxxxxxxxxxxx"  # Change this
REVISION = 1  # Change this, make sure it to current revision
# ====================

getSquareMemberResp = cl.getSquareMember(MEMBER_MID)
squareMember = cl.checkAndGetValue(
                    getSquareMemberResp, 'squareMember', 1)
squareMemberRevision = cl.checkAndGetValue(
                    squareMember, 'revision', 9)
currMembershipState = cl.checkAndGetValue(
                    squareMember, 'membershipState', 7)
REVISION = squareMemberRevision  # Auto patch revision.
print(
    f"Revision: {REVISION}, currMembershipState: {currMembershipState}")

if UPDATE_TYPE == 1:
    """Update member display name."""
    UPDATE_ATTRS = [1]  # DISPLAY_NAME
    DISPLAYE_NAME = input("DisplayName: ")
    print(cl.updateSquareMember(
        UPDATE_ATTRS, UPDATE_PREF_ATTRS,
        MEMBER_MID, SQUAER_MID, REVISION,
        displayName=DISPLAYE_NAME))
elif UPDATE_TYPE == 5:
    """Kick out member."""
    UPDATE_ATTRS = [5]  # MEMBERSHIP_STATE
    MEMBERSHIP_STATE = 5  # KICK_OUT or 6 = BAN
    print(cl.updateSquareMember(
        UPDATE_ATTRS, UPDATE_PREF_ATTRS,
        MEMBER_MID, SQUAER_MID, REVISION,
        membershipState=MEMBERSHIP_STATE))
elif UPDATE_TYPE == 6:
    """Set Co-Admin."""
    UPDATE_ATTRS = [6]  # ROLE
    ROLE = 2  # CO-ADMIN
    print(cl.updateSquareMember(
        UPDATE_ATTRS, UPDATE_PREF_ATTRS,
        MEMBER_MID, SQUAER_MID, REVISION,
        role=ROLE))