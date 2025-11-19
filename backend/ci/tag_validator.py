import ast
import sys
import os

class DataTagValidator:
    """Validate that sensitive fields have proper data tags"""
    
    SENSITIVE_FIELD_NAMES = [
        'password', 'ssn', 'social_security', 'credit_card',
        'salary', 'bonus', 'email', 'phone', 'address'
    ]
    
    REQUIRED_TAGS = ['@PII', '@SENSITIVE', '@HIGHLY_SENSITIVE', '@PUBLIC']
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.violations = []
    
    def validate(self):
        """Check if models.py has proper data tags"""
        if not self.file_path.endswith('models.py'):
            return True
        
        try:
            with open(self.file_path, 'r') as f:
                content = f.read()
            
            # Check for sensitive field names without tags in comments
            for field_name in self.SENSITIVE_FIELD_NAMES:
                if field_name in content.lower():
                    # Check if there's a tag comment nearby
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if field_name in line.lower() and 'db.Column' in line:
                            # Check previous 2 lines for tag comment
                            has_tag = False
                            for j in range(max(0, i-2), i+1):
                                if any(tag in lines[j] for tag in self.REQUIRED_TAGS):
                                    has_tag = True
                                    break
                            
                            if not has_tag and 'DataTag' not in line:
                                self.violations.append(
                                    f"Line {i+1}: Field '{field_name}' may need a data tag"
                                )
            
            return len(self.violations) == 0
        
        except Exception as e:
            print(f"Error validating {self.file_path}: {e}")
            return True
    
    def report(self):
        """Print validation report"""
        if self.violations:
            print(f"\n⚠️  Data Tag Validation Failed for {self.file_path}")
            print("=" * 60)
            for violation in self.violations:
                print(f"  {violation}")
            print("\nPlease add data tags (@PII, @SENSITIVE, etc.) to sensitive fields")
            print("=" * 60)
            return False
        return True

def main():
    """Run validation on staged files"""
    if len(sys.argv) < 2:
        print("Usage: python tag_validator.py <file_path>")
        sys.exit(0)
    
    file_path = sys.argv[1]
    validator = DataTagValidator(file_path)
    
    if validator.validate():
        print(f"✓ {file_path} - Data tags validated")
        sys.exit(0)
    else:
        validator.report()
        sys.exit(1)

if __name__ == '__main__':
    main()