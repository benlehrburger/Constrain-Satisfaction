# Ben Lehrburger
# COSC 076 PA4
import math
import copy
import numpy

# Wrap a CSP solver object for the circuit board problem
class CSP:

    def __init__(self, variables, domains, constraints):

        # Variables list
        self.variables = variables
        # Domains list
        self.domains = domains
        # Constraints list of tuples
        self.constraints = constraints

    # Solve the CSP
    def csp_solver(self):

        # Recursively call the backtrack function
        return self.backtrack(self.getAssignment())

    # Backtrack if we have an inconsistent value choice
    def backtrack(self, assignment):

        # If all variables have been assigned values
        if self.complete(assignment):
            # Print the result in ASCII
            return self.toASCII(assignment, self.variables, self.constraints)

        # Choose a region to assign to based on MRV or DH heuristics
        #region = self.minimumRemainingValue(assignment)
        region = self.degreeHeuristic(assignment)
        # Store the old assignment in case the current is inconsistent
        old_value = assignment[region]

        # Choose the least constraining values in order
        for value in self.leastConstrainingValue(region, assignment):
            # If that value is consistent
            if self.isConsistent(value, region, assignment):

                # Assign it to the current region
                assignment[region] = [value]
                # Check for arc consistency
                consistent = self.arcConsistency(assignment)[0]
                # Get the assignment inferences from arc consistency method
                new_assignment = self.arcConsistency(assignment)[1]

                # If the assignment is arc consistent
                if consistent:
                    # Recursively backtrack
                    result = self.backtrack(new_assignment)

                    # If our assignments are inconsistent
                    if result != 'failure':
                        # Return that we have failed
                        return result

            # If the value is inconsistent assign it to the old value
            else:
                assignment[region] = old_value

        # If we run out of value, return that we have failed
        return 'failure'

    # Check if our assignment is complete
    def complete(self, assignment):

        # Count the number of variables with just 1 assignment
        completeness = 0

        # For each key and value in our assignment
        for key, value in assignment.items():

            # Mark a key as complete if it has only 1 value assigned to it
            if len(value) == 1 or value == []:
                completeness += 1

        # Return true if all variables are assigned
        if completeness == len(self.variables):
            return True

        # Otherwise return false
        return False

    # Check if the current value is consistent with our other assignments
    def isConsistent(self, location, region, assignment):

        # Get variables that have already been assigned
        assigned = self.getAssignedVariables(assignment)

        # Return true if no variables have been assigned
        if len(assigned) == 0:
            return True

        # Get the spaces without a component on them
        available_spaces = self.getAvailableSpaces(assignment)

        # Get the spaces that the current component would take up given the current assignment
        occupied_spaces = []
        for x in range(0, region[0]):
            for y in range(0, region[1]):
                occupied_spaces.append((x + location[0], y + location[1]))

        # Return false f the component would overlap an occupied space
        for space in occupied_spaces:
            if space not in available_spaces:
                return False

        # Return true if the current assignment is not off the board
        if self.within_board(location, region):
            return True

        # Otherwise return false
        else:
            return False

    # Get a list of the least constraining values in increasing order
    def leastConstrainingValue(self, region, assignment):

        # Dictionary of dictionaries
        results = {}

        # For each value in the current region's optional assignments
        for value in assignment[region]:

            # Initialize a new dictionary as the value of the results dictionary
            constraints = {}
            # Make a deepcopy of the current assignment so we can edit it
            assignment_copy = copy.deepcopy(assignment)
            # Simulate what the assignment would look like if we assigned the current value to the region
            simulated_assignment = self.updateAssignment(assignment_copy, region, value)

            # For each unassigned variable
            for unassigned_variable in self.getUnassignedVariables(assignment):

                # Get what potential values remain for that variable after our simulation
                remaining_options = simulated_assignment[unassigned_variable]
                # Add it to that value's dictionary
                constraints[unassigned_variable] = remaining_options

            # Add that value's dictionary to the results dictionary
            results[value] = constraints

        # Store the least constraining values in order
        order = {}

        # For each key and value in the results dictionary
        for value, simulation in results.items():

            # Count how many values remain for that simulation
            value_counter = 0

            # For each key and value in that simulation
            for key, options in simulation.items():

                # If there's no potential values for that region
                if len(options) == 0:
                    # Remove that assignment as an option because it's too constraining
                    del results[value]

                # Otherwise increment the number of remaining values
                else:
                    value_counter += len(options)

            # Add to the order dictionary
            order[value] = value_counter

        # Initialize list to check if each variable still has eligible assignments
        value_check = list(order.values())

        # Return that we have failed if no variables have eligible assignments
        if all(i == 0 for i in value_check):
            return 'Failure'

        # Otherwise order the list from least to most constraining
        least_constraining_order = sorted(order, key=order.get, reverse=True)

        return least_constraining_order

    # Get the minimum remaining value
    def minimumRemainingValue(self, assignment):

        # Get unassigned variables
        unassigned = self.getUnassignedVariables(assignment)
        # Store the first as the MRV
        minimum_remaining_value = unassigned[0]
        # Store that variables restrictions as the number of potential values remaining
        max_restrictions = len(assignment[minimum_remaining_value])

        # For each unassigned variable
        for variable in unassigned:

            # If it has less restrictions than our minimum
            if len(assignment[variable]) < max_restrictions:
                # Store it as the MRV
                minimum_remaining_value = variable
                # Store its restrictions
                max_restrictions = len(assignment[variable])

        return minimum_remaining_value

    # Get the variable involved with the largest number of constraints on other unassigned variables
    def degreeHeuristic(self, assignment):

        # Set available options as high as possible
        available_options = math.inf
        # Set dummy variable to hold subsequently chose region
        most_constraining = None

        # If there's only one unassigned variable left, return it
        if len(self.getUnassignedVariables(assignment)) == 1:
            return self.getUnassignedVariables(assignment)[0]

        # For each unassigned variable
        for unassigned_variable in self.getUnassignedVariables(assignment):

            # Get that variable's assignments
            value = assignment[unassigned_variable]
            # Initialize a counter to count how many assignments would remain for other variables
            available_options_counter = 0

            # For each coordinate in the available assignments
            for coordinate in value:

                # Make a deepcopy of the current assignment so we can edit it
                assignment_copy = copy.deepcopy(assignment)
                # Simulate what the assignment would look like if we assigned the current value to the region
                simulated_assignment = self.updateAssignment(assignment_copy, unassigned_variable, coordinate)

                # Increment the available options counter for each option in the simulation
                for new_key, new_value in simulated_assignment.items():
                    available_options_counter += len(new_value)

            # If the current variable has the least number of available values remaining
            if available_options_counter < available_options:
                # Update the minimum number of options
                available_options = available_options_counter
                # Update the most constraining variable
                most_constraining = unassigned_variable

        return most_constraining

    # Check if the CSP is arc consistent under the current assignment
    def arcConsistency(self, current_assignment):

        # Make a deepcopy of the current assignment so we can edit it
        assignment = copy.deepcopy(current_assignment)

        # Initialize a queue of arcs
        arcs = []

        # For each variable
        for var1 in self.variables.values():
            current_constraints = list(self.variables.values())
            current_constraints.remove(var1)

            # Add an arc between the current variable and every other variable besides itself
            for var2 in current_constraints:
                arcs.append((var1, var2))

        # While the arcs queue is not empty
        while arcs:

            # Remove the first arc
            arc = arcs.pop()
            # Store the coordinates of those arcs
            c1, c2 = arc[0], arc[1]

            # Store boolean as to whether the assignment was revised
            revised = self.removeInconsistentValues(c1, c2, assignment)[0]
            # Store the revised assignment
            assignment = self.removeInconsistentValues(c1, c2, assignment)[1]

            # If the assignment was revised
            if revised:

                # Return false if there are no more values for the current variable
                if len(assignment[c1]) == 0:
                    return False, assignment

        return True, assignment

    # Helper function for the arc consistency method
    def removeInconsistentValues(self, x1, x2, assignments):

        # Boolean to track whether the current assignment was revised or not
        revised = False
        # Store the current arc's coordinates
        c1, c2 = assignments[x1], assignments[x2]
        # Make a deepcopy of the assignment so we can edit it
        domain_copy = copy.deepcopy(assignments)

        # For each value in the first coordinate's domain
        for v1 in c1:

            # If no value in the second coordinate domains satisfies the constraint
            if v1 in c2 and len(c2) == 1:
                # Delete the current coordinate from its domain
                domain_copy[x1].remove(v1)
                # Flag that the assignment was revised
                revised = True

        return revised, domain_copy

    # HELPER FUNCTIONS

    # Updates the assignment given a new region's assigned location
    def updateAssignment(self, current_assignment, region, location):

        # Store the coordinates of that region's assignment
        regional_coordinates = []
        for x in range(0, region[0]):
            for y in range(0, region[1]):
                regional_coordinates.append((location[0] + x, location[1] + y))

        # Make a deepcopy of the assignment so we can edit it
        updated_assignment = copy.deepcopy(current_assignment)

        # Remove the coordinates of that region's assignment from the domains of the other variables
        for key, value in updated_assignment.items():
            for coord in regional_coordinates:
                if coord in value:
                    updated_assignment[key].remove(coord)

        updated_assignment[region] = [location]

        return updated_assignment

    # Get all the positions on circuit board
    def getBoard(self):

        width = self.constraints[0]
        height = self.constraints[1]

        spaces = []

        for x in range(0, width):
            for y in range(0, height):
                spaces.append((x, y))

        return spaces

    # Check if an assignment keeps its component within the board
    def within_board(self, location, region):

        width, height = constraints[0], constraints[1]

        bx, by = location[0], location[1]
        rx, ry = region[0], region[1]

        if bx + rx <= width and by + ry <= height:
            return True
        else:
            return False

    # Get the variables that have already been assigned
    def getAssignedVariables(self, assignment):

        assigned = {}

        for part, place in assignment.items():
            if len(place) == 1:
                assigned[part] = place

        return assigned

    # Get the variables that have no yet been assigned
    def getUnassignedVariables(self, assignment):
        variables = []

        for key, value in assignment.items():
            if len(value) > 1:
                variables.append(key)

        return variables

    # Get the spaces on the board that have not yet been assigned
    def getAvailableSpaces(self, assignment):

        assigned = self.getAssignedVariables(assignment)

        spaces = self.getBoard()

        for part, place in assigned.items():
            regional_coordinates = []
            board_x, board_y = place[0][0], place[0][1]

            for x in range(0, part[0]):
                for y in range(0, part[1]):
                    regional_coordinates.append((board_x + x, board_y + y))

            for coord in regional_coordinates:
                if coord in spaces:
                    spaces.remove(coord)

        return spaces

    # Get the initial domains of each variable at the beggining of the CSP
    def getAssignment(self):

        assignment = {}

        for component in self.variables.values():

            domains = []
            for space in self.getBoard():
                if self.within_board(component, space):
                    domains.append(space)

            assignment[component] = domains
        print(assignment)
        return assignment

    # Output the final assignments in ASCII
    def toASCII(self, output, variables, constraints):

        indexed = {}
        for key, value in output.items():
            for k in self.variables.keys():
                if self.variables[k] == key:
                    indexed[k] = value

        formatted = numpy.full((constraints[1], constraints[0]), '•')
        for key, value in indexed.items():
            dimensions = variables[key]
            for x in range(0, dimensions[0]):
                for y in range(0, dimensions[1]):
                    formatted[y + value[0][1], x + value[0][0]] = key

        print(numpy.array2string(formatted, separator='', formatter={'str_kind': lambda formatted: formatted}))

# PROBLEM 1

# Binary Constraints
width = 10
height = 3

# Constraints
constraints = (width, height)

# Variables
component_a = (3, 2)
component_b = (5, 2)
component_c = (2, 3)
component_e = (7, 1)

variables = {'a': component_a, 'b':component_b, 'c':component_c, 'e': component_e}

# Domains
domains = []

for component in variables.values():
    x, y = component[0], component[1]
    w, h = constraints[0], constraints[1]
    domains.append((w-x, h-y))

circuit_board_problem = CSP(variables, domains, constraints)

print('\nPROBLEM 1 CIRCUIT BOARD')
print('Size: 10 x 3')
print('Number of components: 4\n')
output = circuit_board_problem.csp_solver()

# PROBLEM 2

# Binary Constraints
width = 12
height = 5

# Constraints
constraints = (width, height)

# Variables
component_a = (6, 3)
component_b = (8, 1)
component_c = (3, 4)
component_e = (3, 3)
component_f = (3, 2)
component_g = (5, 1)

variables = {'a': component_a, 'b':component_b, 'c':component_c, 'e': component_e, 'f': component_f, 'g': component_g}

# Domains
domains = []

for component in variables.values():
    x, y = component[0], component[1]
    w, h = constraints[0], constraints[1]
    domains.append((w-x, h-y))

circuit_board_problem = CSP(variables, domains, constraints)

print('\nPROBLEM 2 CIRCUIT BOARD')
print('Size: 12 x 5')
print('Number of components: 6\n')
output = circuit_board_problem.csp_solver()
