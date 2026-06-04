import os
import sys
# Add workspace directory to path to ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Assistant_Module.project_parser import parse_project_description

def test_english_parsing():
    print("Testing English project description parsing...")
    text = (
        "I have a two-floor villa with 6 rooms, 5 air conditioners, around 40 lighting points, "
        "25 socket outlets, and a large kitchen. I might add 1 elevator in the future."
    )
    result = parse_project_description(text)
    
    if "error" in result:
        print(f"❌ English test failed with error: {result['error']}")
        return False
        
    print(f"Parsed Result: {result}")
    
    assert result["building_type"] == "villa", f"Expected villa, got {result['building_type']}"
    assert result["rooms"] == 6, f"Expected 6 rooms, got {result['rooms']}"
    assert result["ac_units"] == 5, f"Expected 5 ac_units, got {result['ac_units']}"
    assert result["lighting_points"] == 40, f"Expected 40 lighting_points, got {result['lighting_points']}"
    assert result["socket_outlets"] == 25, f"Expected 25 socket_outlets, got {result['socket_outlets']}"
    assert result["kitchen"] is True, f"Expected kitchen True, got {result['kitchen']}"
    assert result["future_equipment"]["elevators"] == 1, f"Expected 1 future elevator, got {result['future_equipment']['elevators']}"
    
    print("✓ English parsing test passed successfully!")
    return True

def test_arabic_parsing():
    print("Testing Arabic project description parsing...")
    # "I have an apartment with 3 rooms, two air conditioners, 15 lights, 10 sockets, and a kitchen. In the future, I will install solar systems."
    text = "لدي شقة بها ٣ غرف وتكييفين و١٥ نقطة إضاءة و١٠ مخارج كهرباء ومطبخ. في المستقبل، سأقوم بتركيب أنظمة طاقة شمسية."
    result = parse_project_description(text)
    
    if "error" in result:
        print(f"❌ Arabic test failed with error: {result['error']}")
        return False
        
    print(f"Parsed Result: {result}")
    
    assert result["building_type"] == "apartment", f"Expected apartment, got {result['building_type']}"
    assert result["rooms"] in (3, "3", 3.0), f"Expected 3 rooms, got {result['rooms']}"
    assert result["ac_units"] in (2, "2", 2.0), f"Expected 2 ac_units (dual form), got {result['ac_units']}"
    assert result["lighting_points"] in (15, "15", 15.0), f"Expected 15 lighting_points, got {result['lighting_points']}"
    assert result["socket_outlets"] in (10, "10", 10.0), f"Expected 10 socket_outlets, got {result['socket_outlets']}"
    assert result["kitchen"] is True, f"Expected kitchen True, got {result['kitchen']}"
    assert result["future_equipment"]["solar_systems"] is True, f"Expected solar_systems True, got {result['future_equipment']['solar_systems']}"
    
    print("✓ Arabic parsing test passed successfully!")
    return True

if __name__ == "__main__":
    # Ensure GEMINI_API_KEY is available
    if not os.environ.get("GEMINI_API_KEY"):
        print("⚠️ Warning: GEMINI_API_KEY environment variable is not set. The tests will likely fail if no key is present.")
        
    en_ok = test_english_parsing()
    print("-" * 50)
    ar_ok = test_arabic_parsing()
    
    if en_ok and ar_ok:
        print("\n🎉 All automated parsing tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
