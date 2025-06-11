


for parent in output/one_platoon output/two_platoon; do
  for subdir in "$parent"/*/; do
    # Only act if it is a directory
    if [ -d "$subdir" ]; then
      # Delete all files (not folders) inside the subdirectory
      find "$subdir" -type f -delete
    fi
  done
done

for parent in output_transitory/one_platoon output_transitory/two_platoon; do
  for subdir in "$parent"/*/; do
    # Only act if it is a directory
    if [ -d "$subdir" ]; then
      # Delete all files (not folders) inside the subdirectory
      find "$subdir" -type f -delete
    fi
  done
done
