#!/usr/bin/env python3

import os
from termcolor import colored

# Gets the absolute path of the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Input file path
input_file_path = os.path.join(PROJECT_ROOT, "input", "III_main_scm_1.1.txt") # GTA III (Original) SCM file path

# Output directory files paths
mission_waits_dir = os.path.join(PROJECT_ROOT, "output", "Mission_Waits") # Mission_Waits directory path
trivial_dupes_dir = os.path.join(PROJECT_ROOT, "output", "Trivial_Dupes") # Trivial_Dupes directory path
missions_compatibilities_dir = os.path.join(PROJECT_ROOT, "output", "Missions_Compatibilities") # Missions_Compatibilities directory path

# Ensures that output directories exist
os.makedirs(mission_waits_dir, exist_ok=True) # Creates the Mission_Waits directory if it doesn't exist
os.makedirs(trivial_dupes_dir, exist_ok=True) # Creates the Trivial_Dupes directory if it doesn't exist
os.makedirs(missions_compatibilities_dir, exist_ok=True) # Creates the Missions_Compatibilities directory if it doesn't exist

# Output files paths 
output_file_missions_waits = os.path.join(mission_waits_dir, "mission_waits_output.txt") # Mission waits output file path
output_file_trivial_dupes = os.path.join(trivial_dupes_dir, "trivial_dupes_output.txt") # Trivial dupes output file path
output_file_missions_compatibilities = os.path.join(missions_compatibilities_dir, "missions_compatibilities_output.txt") # Missions compatibilities output file path

""" Functions """

# Function to save mission stacks data to a file
def SaveMissionStacksToFile(output_path, mission_stacks):
    # Opens the output file in write mode
    with open(output_path, "w") as file:
        # Writes the headers
        headers = "{:<40}{:<15}".format("Mission Name", "Stack (Local Offset)") # Headers with wider spacing
        
        file.write(headers + "\n")
        
        # Adds a separator line below the headers
        file.write("=" * 55 + "\n")  
        
        # Writes the mission stacks data
        for mission, stack in mission_stacks.items():
            row = "{:<40}{:<15}".format(mission, stack) # Formats the row with the mission name and the stack
            
            file.write(row + "\n")

# Function to get all the mission stacks from the GTA SCM file
def GetMissionStacks(file_path):
    # Dictionary to store the mission stacks
    mission_stacks = {}
    
    # Variable to store the current mission
    current_mission = None
    
    # Variable to check if the current line is inside a mission block
    in_mission = False
    
    # Opens the SCM file in read mode
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    # Iterates through the lines to extract the mission stacks
    i = 0
    
    # Iterates through the lines
    while i < len(lines):
        line = lines[i].strip() # Removes the leading and trailing whitespaces

        # Checks for mission block start
        if line.startswith("//-------------Mission"):
            in_mission = True # Sets the in_mission flag to True
            current_mission = "Unknown Mission" # Sets the current mission to "Unknown Mission"
            
            # Checks for the mission name in next line
            if i + 1 < len(lines):
                mission_line = lines[i + 1].strip() # Extracts the mission line
                
                # Checks if the mission line contains the mission name
                if mission_line.startswith("// Originally:"):
                    current_mission = mission_line.split(":", 1)[1].strip() # Extracts the mission name
                    i += 1  # Skips the mission name line        
            continue

        # Resets at end of mission block
        if line.startswith("//-------------") and in_mission:
            in_mission = False # Sets the in_mission flag to False
            current_mission = None # Resets the current mission

        # Looks for the gosub in mission block
        if in_mission and current_mission:
            # Checks for the  gosub line
            if "0050: gosub" in line:
                # Checks next line for valid offsets
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip() # Extracts the next line
                    
                    # Checks if the next line contains both "{" and "}"
                    if "{" in next_line and "}" in next_line:
                        offset_part = next_line.split("}")[0].strip("{").strip() # Extracts the numbers between "{}"
                        offsets = offset_part.split() # Splits the offset part
                        
                        # Ensures that the line has exactly two integer numbers
                        if len(offsets) == 2 and all(o.isdigit() for o in offsets):
                            mission_stacks[current_mission] = offsets[1] # Adds the mission stack to the dictionary
                            in_mission = False # Sets the in_mission flag to False
                        else:
                            # Prints a warning message if the offset format is invalid
                            print(colored(f"⚠️ Invalid offset format in mission '{current_mission}' at line {i+1}", "yellow"))
                
                # Skips the next line
                i += 1 
                
        # Increments the index 
        i += 1
    
    # Returns the mission stacks dictionary
    return mission_stacks

# Function to get all the lines from a GTA SCM file
def GetAllLines(file_path):
    # List to store all lines with offsets and mission names
    all_lines = []
    
    # Variable to store the current mission name
    current_mission = "Unknown Mission"
    
    # Opens the SCM file in read mode
    with open(file_path, "r") as file:
        # Iterates through the lines to extract the global and local offsets
        for line in file:
            # Checks if the line indicates a mission name
            if line.startswith("// Originally:"):
                current_mission = line.split(":", 1)[1].strip() # Extracts the mission name 
                
            # Checks if the line contains both "{" and "}"
            if "{" in line and "}" in line:
                offsets = line.split("}")[0].strip("{").split() # Extracts the numbers between "{}" (Offsets)
                # Ensures that the line has exactly two integer numbers
                if len(offsets) == 2:
                    global_offset, local_offset = offsets # Extracts the global and local offsets 
                    # Appends the line data with the current mission name                        
                    all_lines.append(((global_offset, local_offset), line.strip(), current_mission)) # Appends the global and local offsets with the line and the current mission name
    
    # Returns all the lines with their global and local offsets and mission 
    return all_lines

# Function to save mission waits data to a file
def SaveMissionWaitsDataToFile(output_path, results, missions_waits_count):
    # Opens the output file in write mode
    with open(output_path, "w") as file:
        # Writes the headers with wider spacing
        headers = "{:<15}{:<40}{:<40}{:<40}{:<40}{:<40}".format(
            "Wait Number", # Wait Number Header
            "Global Offset of the Wait Instruction", # Global Offset of the Wait Instruction Header
            "Local Offset of the Wait Instruction", # Local Offset of the Wait Instruction Header
            "Global Offset of the Next Instruction", # Global Offset of the Next Instruction Header
            "Local Offset of the Next Instruction", # Local Offset of the Next Instruction Header
            "Mission Name" # Mission Name Header
        )
        
        # Writes the headers
        file.write(headers + "\n")
        
        # Adds a separator line below the headers
        file.write("=" * 215 + "\n")  
        
        # Prints total missions_waits_count (optional)
        print(f"Total Missions Waits Count: {missions_waits_count}\n")

        # Variables to track the current mission and wait number
        current_mission = None
        wait_number = 0
        
        # Iterates through the results to write the data rows
        for index, (wait_offsets, next_instruction_offsets, mission_name) in enumerate(results, start=1):
            # Checks if the mission has changed
            if mission_name != current_mission:
                # Resets the wait number counter
                wait_number = 0
                
                # Updates the current mission
                current_mission = mission_name
            
            # Increments the wait number for the current mission
            wait_number += 1
            
            # Formats the row
            row = "{:<15}{:<40}{:<40}{:<40}{:<40}{:<40}".format(
                wait_number, # Wait Number (resets for each mission
                wait_offsets[0], # Global Offset of the Wait Instruction
                wait_offsets[1], # Local Offset of the Wait Instruction
                next_instruction_offsets[0], # Global Offset of the Next 
                next_instruction_offsets[1], # Local Offset of the Next 
                mission_name # Mission Name
            )
            
            # Writes the data rows to the file
            file.write(row + "\n")

# Function to save trivial dupes data to a file
def SaveTrivialDupesDataToFile(output_path, matching_offsets, mission_stacks):
    # Opens the output file in write mode
    with open(output_path, "w") as file:
        # Writes matching offsets section
        if matching_offsets:
            file.write("Matching trivial dupes found:\n\n")
            # Iterates through the matching offsets and writes them to the file
            for local_offset, cases in matching_offsets.items():
                file.write(f"Local Offset: {local_offset}\n")
                # Iterates through the cases and writes them to the file
                for idx, case in enumerate(cases, start=1):
                    # Extracts the cases
                    ((wait_offsets1, next_instr1, mission1), (other_offsets, _, mission2)) = case
                    file.write(f"  Case {idx}:\n") # Writes the case number
                    file.write(f"    From Wait (Mission: {mission1}, Stack: {mission_stacks.get(mission1)}):\n") # Writes the first mission with the stack
                    file.write(f"      Global Offset: {wait_offsets1[0]}, Local Offset: {wait_offsets1[1]}\n") # Writes the global and local offsets of the wait instruction
                    file.write(f"      Next Instruction: Global Offset: {next_instr1[0]}, Local Offset: {next_instr1[1]}\n") # Writes the global and local offsets of the next instruction
                    file.write(f"    Matches With (Mission: {mission2}, Stack: {mission_stacks.get(mission2)}):\n") # Writes the second mission with the stack
                    file.write(f"      Global Offset: {other_offsets[0]}, Local Offset: {other_offsets[1]}\n\n") # Writes the global and local offsets of the matching case
        else:
            # Writes that no matching local offsets were found
            file.write("No matching local offsets found.\n")

# Function to find matching local offsets
def FindMatchingLocalOffsets(results, all_lines):
    # Dictionary to store the matching local offsets
    offsets_matches = {}
    
    # Creates a dictionary to map local offsets to their corresponding lines and mission names
    local_offset_map = {int(line_data[0][1]): line_data for line_data in all_lines}
    
    # Iterates through all lines to create the map
    for wait_offsets, next_instr_offsets, mission_name in results:
        local_offset1 = int(next_instr_offsets[1])
        if local_offset1 in local_offset_map:
            # Extracts the correct offsets from the local_offset_map
            matching_line_data = local_offset_map[local_offset1] # Matching line data
            matching_global_offset = matching_line_data[0][0]  # Global offset of the matching line
            matching_local_offset = matching_line_data[0][1]  # Local offset of the matching line
            matching_mission_name = matching_line_data[2]  # Mission name of the matching line
            
            # Checks if the matching offsets are different from the current wait offsets
            if matching_global_offset != wait_offsets[0]:  
                # Creates the matching offsets tuple with only the offset values
                matching_offsets = (matching_global_offset, matching_local_offset)
                offsets_matches.setdefault(local_offset1, []).append((
                    (wait_offsets, next_instr_offsets, mission_name), # Current wait offsets
                    (matching_offsets, None, matching_mission_name)   # Matching offsets
                ))
    
    # Returns the dictionary with the matching local offsets
    return offsets_matches

# Function to print the results of the waits offsets and the next instruction of the wait offsets
def PrintResults(results, count, matching_offsets, mission_stacks):
    print(colored("There are {} mission waits in the SCM.".format(count), "yellow"))
    
    print("")

    # Prints all the waits details
    for index, (wait_offsets, next_instruction_offsets, mission_name) in enumerate(results, start=1):
        print(colored(f"Wait N°{index} (Mission: {mission_name}):", "cyan")) # Prints the wait number and the mission name
        
        print("  Global Offset of the Wait Instruction: {}".format(wait_offsets[0])) # Prints the Global Offset of the Wait Instruction
        print("  Local Offset of the Wait Instruction: {}".format(wait_offsets[1])) # Prints the Local Offset of the Wait Instruction
        print("  Global Offset of the Next Instruction: {}".format(next_instruction_offsets[0])) # Prints the Global Offset of the Next Instruction
        print("  Local Offset of the Next Instruction: {}".format(next_instruction_offsets[1])) # Prints the Local Offset of the Next Instruction
        
        print("")
        
    # Prints matching offsets section
    if matching_offsets:
        print(colored("The matching local offsets found in this SCM are:", "yellow"))
        # Iterates through the matching offsets and prints them
        for local_offset, cases in matching_offsets.items():
            print(colored(f"Local Offset: {local_offset}", "cyan"))
            # Iterates through the cases and prints them
            for idx, case in enumerate(cases, start=1):
                ((wait_offsets1, next_instr1, mission1), (other_offsets, _, mission2)) = case
                print(colored(f"  Case {idx}:", "green")) # Prints the case number
                print(f"    From Wait (Mission: {mission1}):") # Prints the mission name
                print(f"      Mission Stack (Local Offset after first gosub): {mission_stacks[mission1]}") # Prints the mission stack of the first mission
                print(f"      Global Offset: {wait_offsets1[0]}, Local Offset: {wait_offsets1[1]}") # Prints the Global and Local Offsets of the Wait Instruction
                print(f"      Next Instruction: Global Offset: {next_instr1[0]}, Local Offset: {next_instr1[1]}") # Prints the Global and Local Offsets of the Next Instruction
                print(f"    Matches With (Mission: {mission2}):") # Prints the mission name that matches with the previous one
                print(f"      Mission Stack (Local Offset after first gosub): {mission_stacks[mission2]}") # Prints the mission stack of the second mission
                print(f"      Global Offset: {other_offsets[0]}, Local Offset: {other_offsets[1]}") # Prints the Global and Local Offsets of the matching instruction
                
                print("")
    else:
        # Prints that no matching local offsets were found
        print(colored("No matching local offsets found.", "red"))
        
        print("")

# Function to count the number of mission waits
def MissionsWaitsCounter(file_path):
    # Variable to store the count of mission waits
    missions_waits_count = 0
    
    # Opens the SCM file in read mode and iterates through the lines to count the valid lines
    with open(file_path, "r") as file:
        # Iterates through the lines in the file
        for line in file:
            # Checks if the line contains the 'wait' instruction
            if "} 0001: wait" in line:
                offsets = line.split("}")[0].strip("{").split() # Extracts the numbers between "{}"
                
                # Ensures that the line has exactly two integer numbers
                if len(offsets) == 2 and all(num.isdigit() for num in offsets):
                    missions_waits_count  += 1  # Increments the count of waits lines
                    
    # Returns the count of waits lines that has 2 numbers between brackets              
    return missions_waits_count 

# Function to get wait instructions from SCM file
def GetWaitsLines(file_path):
    # List to store the waits results1
    waitsresults = []
    
    # Variable to store the current mission name
    current_mission = "Unknown Mission"
    
    # Opens the SCM file in read mode
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines() # Reads all the lines from the file
    
    # Iterates through the lines
    for i, line in enumerate(lines):
        # Checks if the line indicates a mission name
        if line.strip().startswith("// Originally:"):
            current_mission = line.split(":", 1)[1].strip() # Extracts the mission name
        
        # Checks if the line contains the 'wait' instruction
        if "} 0001: wait" in line:
            wait_line_offsets = line.split("}")[0].strip("{").split()  # Extracts offset numbers from the wait instruction line
            
            # Ensures the wait line has exactly two numbers
            if len(wait_line_offsets) == 2 and i + 1 < len(lines):
                next_instruction_of_wait_line = lines[i + 1].strip() # Extracts the next instruction line
                
                # Validates next instruction contains '}' and if isn't empty
                if "}" in next_instruction_of_wait_line and next_instruction_of_wait_line:
                    next_instruction_of_wait_line_offsets = next_instruction_of_wait_line.split("}")[0].strip("{").split() # Extracts numbers from the next instruction line
                    
                    # Ensures the next instruction also has two numbers
                    if len(next_instruction_of_wait_line_offsets) == 2:
                        waitsresults.append((wait_line_offsets, next_instruction_of_wait_line_offsets, current_mission)) # Appends the wait line and the next instruction line with the current mission name
    
    # Sorts the results by global offset
    waitsresults.sort(key=lambda x: int(x[0][0]))
    
    # Returns the wait instructions with their next instructions and mission names
    return waitsresults

""" Main Program """

print(colored("Starting the script...", "cyan"))

print("")

print(colored("Processing GTA III (Original) SCM file...", "yellow"))

print("")

print(colored("Getting all the waits offsets and the next instruction of the wait offsets from the GTA III (Original) SCM file...", "yellow"))

print("")

# Calls the function to count lines with '} 0001: wait' on the from the SCM file
missions_waits_count = MissionsWaitsCounter(input_file_path)

# Calls the function to get the waits offsets (globals and locals) and the next instruction of the wait offsets (globals and locals) from the SCM file
waitsoffsets = GetWaitsLines(input_file_path)

print("")

print(colored("Getting all the mission stacks from the GTA III (Original) SCM file...", "yellow"))

print("")

# Calls the function to get all the mission stacks from the GTA SCM file 
mission_stacks = GetMissionStacks(input_file_path)

print("")

print(colored("Getting all the Trivial Dupes from the GTA III (Original) SCM file...", "yellow"))

print("")

# Calls the function to get all the lines from the GTA SCM file
all_lines_from_scm = GetAllLines(input_file_path)

# Calls the function to find and group the matching local offsets from the GTA SCM file
matching_offsets = FindMatchingLocalOffsets(waitsoffsets, all_lines_from_scm)

# Prints the results (calling the function)
PrintResults(waitsoffsets, missions_waits_count, matching_offsets, mission_stacks)

# Calls the function to save the mission waits data to a file
SaveMissionWaitsDataToFile(output_file_missions_waits, waitsoffsets, missions_waits_count)

# Calls the function to save the mission stacks data to a file
SaveMissionStacksToFile(output_file_missions_compatibilities, mission_stacks)

# Calls the function to save the trivial dupes data to a file
SaveTrivialDupesDataToFile(output_file_trivial_dupes, matching_offsets, mission_stacks)

# Prints where the output file of the mission waits was saved
print(colored(f"Missions waits saved to: {output_file_missions_waits}", "green"))

print("")

# Prints where the output file of the missions compatibilities was saved
print(colored(f"Missions compatibilities saved to: {output_file_missions_compatibilities}", "green"))

print("")

# Prints where the output file of the trivial dupes was saved
print(colored(f"Trivial dupes saved to: {output_file_trivial_dupes}", "green"))

print("")

# Prints that the execution was completed
print(colored("Execution completed!", "green"))

print("")

input("Press any key to continue...")