from db.database import SessionLocal
from db.models import Invitation

def check_invitation(token_to_check):
    db = SessionLocal()
    
    try:
        print(f"Checking for token: {token_to_check}")
        invitation = db.query(Invitation).filter(Invitation.Token == token_to_check).first()
        
        if invitation:
            print(f"FOUND: ID={invitation.Id}, Email={invitation.Email}, Token={invitation.Token}, GoalId={invitation.GoalId}")
        else:
            print("NOT FOUND")
            
        print("\nAll Invitations:")
        all_invites = db.query(Invitation).all()
        for inv in all_invites:
            print(f"- ID={inv.Id}, Token={inv.Token}, Email={inv.Email}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_invitation('60097be5-6aef-4451-b5d3-2efe3cf82b33')
