# Ben Lehrburger
# COSC 076 PA4
import copy

# Wrap a CSP solver object for the map problem
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
        return self.backtrack(self.get_assignment())

    # Backtrack if we have an inconsistent value choice
    def backtrack(self, assignment):

        # If all variables have been assigned values
        if self.complete(assignment):
            # Print the formatted result
            return self.format(assignment)

        # Choose a region to assign to based on MRV or DH heuristics
        #region = self.minimumRemainingValue(assignment)
        region = self.degreeHeuristic(assignment)
        # Store the old assignment in case the current is inconsistent
        old_value = assignment[region]

        # Choose the least constraining values in order
        for value in self.leastConstrainingValue(assignment, region):
            # If that value is consistent
            if self.isConsistent(value, region, assignment):

                # Assign it to the current region
                assignment[region] = value
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

    # Check if the current value is consistent with our other assignments
    def isConsistent(self, value, domain, assignment):

        # Store the local constraints
        local_constraints = []

        # For each constraint
        for constraint in self.constraints:
            # If the current domain is in that constraint
            if domain in constraint:
                # Add it as a local constraint
                local_constraints.append(constraint)

        # For each local constraint
        for local_constraint in local_constraints:
            # For each variable in local constraints
            for region in local_constraint:
                # Return false f a neighbor has the same color as the current value
                if assignment[region] == value and region is not domain:
                    return False

        # Otherwise return true
        return True

    # Check if our assignment is complete
    def complete(self, assignment):

        # Count the number of variables with just 1 assignment
        completeness = 0

        # For each key and value in our assignment
        for key, value in assignment.items():

            # Mark a key as complete if it has only 1 value assigned to it
            if len(value) == 1:
                completeness += 1

        # Return true if all variables are assigned
        if completeness == len(self.variables):
            return True

        # Otherwise return false
        return False

    # Get the minimum remaining value
    def minimumRemainingValue(self, assignment):

        # Get unassigned variables
        unassigned = self.pickUnassignedVariables(assignment)
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

        # Set dummy variable to hold subsequently chose region
        heuristic = None
        # Max degree of constraints is initially 0
        max_degree = 0
        # Get unassigned variables
        unassigned = self.pickUnassignedVariables(assignment)

        # For each unassigned variable
        for region in unassigned:

            # Degree counter is initially 0
            current_degree = 0

            # For each constraint
            for constraint in self.constraints:

                # Increment the degree counter if the current region is involved with that constraint
                if region in constraint:
                    current_degree += 1

            # If that variable has the greatest number of constraints on other variables
            if current_degree >= max_degree:
                # Update the maximum degree
                max_degree = current_degree
                # Update the most constraining variable
                heuristic = region

        return heuristic

    # Get a list of the least constraining values in increasing order
    def leastConstrainingValue(self, assignment, region):

        # Get the current region's neighbors
        neighbors = self.getNeighbors(region)
        # Track how many times the value is implicated
        frequencies = []
        # Store its possible assignments
        possible_values = assignment[region]

        # For each neighbor
        for neighbor in neighbors:

            # If that neighbor already has an assignment and it's one of the current region's possible assignments
            if len(assignment[neighbor]) == 1 and assignment[neighbor] in possible_values:
                # Remove that value from the region's possible assignments
                possible_values.remove(assignment[neighbor])

        # Return that we failed if there are no more possible assignments
        if len(possible_values) == 0:
            return 'failure'

        # Return assignment if there's only one possible value
        elif len(possible_values) == 1:
            return possible_values[0]

        # The assignment can be anything if there are no neighbors
        elif not neighbors:
            return possible_values

        # Otherwise if there are possible assignments
        else:

            # For each neighbor
            for neighbor in neighbors:
                # For each possible neighboring value
                for value in assignment[neighbor]:

                    # If that value is a possible value in the current region
                    if value in possible_values:
                        # Add it to the frequencies list
                        frequencies.append(value)

            # Initialize a list to hold the values in order
            value_order = []

            # While there are still value constraints
            while len(frequencies) > 0:

                # Grab the least constraining value
                least_constraining = min(frequencies, key=frequencies.count)

                # Append it to our list of values in order
                if least_constraining not in value_order:
                    value_order.append(least_constraining)

                # Delete that value from the frequency tracker
                try:
                    while True:
                        frequencies.remove(least_constraining)
                except ValueError:
                    pass

            return value_order

    # Check if the CSP is arc consistent under the current assignment
    def arcConsistency(self, curr_domain):

        # Make a deepcopy of the current domain so we can edit it
        domain = copy.deepcopy(curr_domain)

        # Initialize a queue of arcs
        arcs = []

        # Populate the queue with each set of constraints
        for constraint in self.constraints:
            if len(constraint) > 1:
                arcs.append(constraint)

        # While the arcs queue is not empty
        while arcs:

            # Remove the first arc
            arc = arcs.pop()
            # Store the coordinates of those arcs
            x1, x2 = arc[0], arc[1]

            # Store boolean as to whether the assignment was revised
            revised = self.removeInconsistentValues(x1, x2, domain)[0]
            # Store the revised assignment
            domain = self.removeInconsistentValues(x1, x2, domain)[1]

            # If the assignment was revised
            if revised:

                # Return false if there are no more values for the current variable
                if len(domain[x1]) == 0:
                    return False, domain

                # Remove the constraining variable from the current coordinate's list of neighbors
                neighbors = self.getNeighbors(x1)
                neighbors.remove(x2)

                # Add every other neighbor to the queue
                for neighbor in neighbors:
                    arcs.append((neighbor, x1))

        return True, domain

    # Helper function for the arc consistency method
    def removeInconsistentValues(self, x1, x2, curr_domain):

        # Boolean to track whether the current assignment was revised or not
        revised = False
        # Store the current arc's coordinates
        d1, d2 = curr_domain[x1], curr_domain[x2]
        # Make a deepcopy of the assignment so we can edit it
        domain_copy = copy.deepcopy(curr_domain)

        # For each value in the first coordinate's domain
        for v1 in d1:

            # If no value in the second coordinate domains satisfies the constraint
            if v1 in d2 and len(d2) == 1:
                # Delete the current coordinate from its domain
                domain_copy[x1].remove(v1)
                # Flag that the assignment was revised
                revised = True

        return revised, curr_domain

    # HELPER FUNCTIONS

    # Get the string versions of keys and values
    def encode(self, string):

        if string == 'sa':
            return 'South Australia'
        if string == 'wa':
            return 'Western Australia'
        if string == 'nt':
            return 'Northern Territory'
        if string == 'q':
            return 'Queensland'
        if string == 'nsw':
            return "New South Wales"
        if string == 'v':
            return 'Victoria'
        if string == 't':
            return 'Tasmania'
        if string == 'r':
            return 'red'
        if string == 'g':
            return 'green'
        if string == 'b':
            return 'blue'

    # Format the outputted assignment
    def format(self, assignment):

        for key, value in assignment.items():
            print('The region ' + str(self.encode(key)) + ' is colored ' + str(self.encode(value)))

    # Get the neighboring nodes of a region
    def getNeighbors(self, region):

        neighbors = []

        for constraint in self.constraints:
            if region in constraint:
                for sub_region in constraint:
                    if sub_region is not region:
                        neighbors.append(sub_region)

        return neighbors

    # Get the initial domains of each variable at the beggining of the CSP
    def get_assignment(self):
        assignment = {}

        for variable in self.variables:
            assignment[variable] = copy.deepcopy(self.domains)

        return assignment

    # Get the variables that have no yet been assigned
    def pickUnassignedVariables(self, assignment):
        variables = []

        for key, value in assignment.items():
            if len(value) > 1:
                variables.append(key)

        return variables

# Binary Constraints
c1 = ('wa', 'sa')
c2 = ('wa', 'nt')
c3 = ('sa', 'nt')
c4 = ('nt', 'q')
c5 = ('sa', 'q')
c6 = ('q', 'nsw')
c7 = ('sa', 'nsw')
c8 = ('nsw', 'v')
c9 = ('sa', 'v')
c10 = ('t')

# Constraints
constraints = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

# Variables
variables = ['sa', 'wa', 'nt', 'q', 'nsw', 'v', 't']

# Domains
domains = ['r', 'g', 'b']

map_problem = CSP(variables, domains, constraints)

print(map_problem.csp_solver())
