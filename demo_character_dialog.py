"""Quick visual demo of the character dialog enhancements."""
import sys
from PySide6.QtWidgets import QApplication
from nico.presentation.widgets.character_dialog import CharacterDialog
from nico.application.context import get_app_context


def demo_character_dialog():
    """Launch the enhanced character dialog."""
    
    # Initialize app context
    app_context = get_app_context()
    
    # Create Qt application
    qt_app = QApplication.instance() or QApplication(sys.argv)
    
    # Show the character dialog for project 1
    dialog = CharacterDialog(project_id=1)
    
    print("\n" + "="*70)
    print("CHARACTER DIALOG DEMO")
    print("="*70)
    print("\nEnhancements to try:")
    print("  1. First Name dropdown: 452 names (type to search)")
    print("  2. Last Name dropdown: 245 surnames")
    print("  3. Occupation dropdown: 5,798 government occupations!")
    print("  4. 🎲 Random buttons next to each field")
    print("\nTips:")
    print("  • Start typing to filter options")
    print("  • Press 🎲 for instant random selection")
    print("  • Use arrow keys to navigate filtered results")
    print("  • You can still type custom values")
    print("\nTry searching for:")
    print("  • Names starting with 'El'")
    print("  • Surnames containing 'son'")
    print("  • Occupations with 'teacher' or 'engineer'")
    print("="*70 + "\n")
    
    # Show dialog
    if dialog.exec():
        print("\n✓ Character saved!")
    else:
        print("\n✗ Dialog cancelled")
    
    qt_app.quit()


if __name__ == "__main__":
    try:
        demo_character_dialog()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted")
        sys.exit(0)
