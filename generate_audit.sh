#!/bin/bash
OUTPUT_FILE="project_audit.txt"
echo "=== SMARTFURNITUREWB AUDIT ===" > $OUTPUT_FILE
echo "--- DIRECTORY STRUCTURE ---" >> $OUTPUT_FILE
# جلب شجرة الملفات متجاهلاً ملفات الكاش
find . -type f -not -path "*/__pycache__/*" -not -path "*/.git/*" -not -name "*.pyc" | sort >> $OUTPUT_FILE

echo -e "\n--- CORE FILES CONTENT (First 30 lines) ---" >> $OUTPUT_FILE
# قراءة بدايات الملفات البرمجية لفهم المعمارية
for f in $(find . -maxdepth 3 -name "*.py" -not -path "*/__pycache__/*"); do
    echo -e "\n>>> File: $f" >> $OUTPUT_FILE
    head -n 30 "$f" >> $OUTPUT_FILE
    echo "<<<" >> $OUTPUT_FILE
done

echo "Audit completed. File generated: $OUTPUT_FILE"
