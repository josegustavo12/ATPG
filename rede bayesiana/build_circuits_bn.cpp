// tutorial1.cpp
// Tutorial1 creates a simple network with three nodes,
// then saves it as XDSL file to disk.

// g++ -std=c++11 main.cpp tutorial?.cpp -I./smile -L./smile -lsmile  <<<<< ------- 
// g++ build_circuits_bn.cpp -I./include -L./lib -lsmile -o build_circuits_bn


#include "include/smile.h"
#include "include/smile_license.h"
#include <cstdio>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <unistd.h>
#include <math.h>



static int CreateCptNode(
    DSL_network& net, const char* id, const char* name,
    std::initializer_list<const char*> outcomes, int xPos, int yPos);



void writeToFile(const std::vector<std::vector<std::string>>& vecOfVecs, const std::string& filename) {
    std::ofstream outFile(filename); // Open the file for writing
    if (!outFile.is_open()) { // Check if the file is opened successfully
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }

    // Write the contents of the vector of vectors to the file
    for (const auto& innerVec : vecOfVecs) {
        for (const auto& str : innerVec) {
            outFile << str << " ";
        }
        outFile << std::endl; // Write newline after each inner vector
    }

    // Close the file
    outFile.close();
}



std::vector<std::vector<std::string>>  read_verilog(const std::string& verilogFilePath) {
    // Open the Verilog file
    std::ifstream verilogFile(verilogFilePath);
    // Vector where my data will be add
    std::vector<std::vector<std::string>> Data_Vector;
    std::vector<std::string> tempVector;


    // Check if the file is opened successfully
    if (!verilogFile.is_open()) {
        std::cerr << "Error opening file: " << verilogFilePath << std::endl;
        std::vector<std::vector<std::string>> null;
        return null;
    }

    // Read the Verilog file line by line
    std::string line;
   while (std::getline(verilogFile, line)) {
        // Find the first opening parenthesis
        size_t ParenthesisPos = line.find('(');
        if((ParenthesisPos != std::string::npos) && (ParenthesisPos < 5)){

            std::string LogicArgument = line.substr(0, ParenthesisPos);
            tempVector.push_back(LogicArgument);
            // std::cout << "LogicArgument: " << LogicArgument << std::endl;

            // std::cout << "Logic Argument: " << LogicArgument << std::endl;
            size_t current =  ParenthesisPos;
             while (current != std::string::npos + 1) { 
                size_t commaPos = line.find(',', current);
                if(commaPos == std::string::npos){
                     size_t ParenthesisPos_last = line.find(')', current);
                     std::string Argument = line.substr(current + 1, ParenthesisPos_last - current - 1);
                    // std::cout << "Argument: " << Argument << std::endl;
                     tempVector.push_back(Argument);
                     // std::cout << "Argument: " << Argument << std::endl; //get end argument
                     break;

                }
                std::string Argument = line.substr(current + 1, commaPos - current - 1);
                tempVector.push_back(Argument);
                // std::cout << "Argument: " << Argument << std::endl;
                current = commaPos + 1;
                
                
            
             }
            Data_Vector.push_back(tempVector);
            tempVector.clear();      
        }
        
    
    
    
    }

    // Close the file
    verilogFile.close();
    return Data_Vector;
}


std::vector<std::string>  get_children_from_node(const std::string& node, const std::vector<std::vector<std::string>>& nodes) {

       std::vector<std::string> result;

         for (const auto& vec : nodes) {
                int k = 0;
                std::string aux; 
                for (const auto& str : vec) {
                    if(k == 1){
                        if(str == node){break;}
                        else{
                            aux = str;
                        } 
                    }
                    if(k > 1 && str == node){
                        result.push_back(aux);
                        //std::cout << "children of " << node << " is " << aux << std::endl;
                    }
                    k++;
                    }}
       return result;

}

// Function to print the nested vector
void print_verilog_nodes(const std::vector<std::vector<std::string>>& nodes) {
    for (const auto& row : nodes) {
        for (const auto& element : row) {
            std::cout << element << " ";
        }
        std::cout << std::endl;
    }
}


std::vector<std::string>  get_inputs(const std::string& verilogFilePath) {
    // Open the Verilog file
    std::ifstream verilogFile(verilogFilePath);
    // Vector where my data will be add
    std::vector<std::string> input_Vector;


    // Check if the file is opened successfully
    if (!verilogFile.is_open()) {
        std::cerr << "Error opening file: " << verilogFilePath << std::endl;
        std::vector<std::vector<std::string>> null;
        return {};
    }

    // Read the Verilog file line by line
    std::string line;
    int currentLine = 0;
   while (std::getline(verilogFile, line)) {
       
       
        if (currentLine == 2) {
            size_t lstcommaPos = 5;
            size_t currentcommaPos = 0;
            while (currentcommaPos != std::string::npos){
                  currentcommaPos = line.find(',',lstcommaPos);
                  std::string input = line.substr(lstcommaPos + 1, currentcommaPos - lstcommaPos - 1);
                  input_Vector.push_back(input);
                  lstcommaPos = currentcommaPos + 1;
            }
            
        } 
    currentLine = currentLine + 1;
   }
   
   // Close the file
    verilogFile.close();
    return input_Vector;

   }


// building logic table // first part - generate the matrix only

// Function prototype
void generate_truth_table(int num_vars);

int** generate_truth_table(int num_vars, int* num_rows) {
    *num_rows = (int)pow(2, num_vars); // Number of rows in the truth table
    int cols = num_vars; // Number of columns (one for each variable)
   
    // Allocate memory for the truth table
    int** truth_table = (int**)malloc(*num_rows * sizeof(int*));
    for (int i = 0; i < *num_rows; i++) {
        truth_table[i] = (int*)malloc(cols * sizeof(int));
    }

    // Generate the truth table
    for (int i = 0; i < *num_rows; i++) {
        for (int j = 0; j < cols; j++) {
            truth_table[i][j] = (i >> (cols - j - 1)) & 1; // Extracting each bit of i
        }
    }

    return truth_table;
};

int* process_truth_table(int** truth_table, int num_rows, int num_vars, const char* operation) {
    int* results = (int*)malloc(num_rows * sizeof(int)); // Allocate memory for the results array

    //printf("Processing truth table with operation: %s\n", operation);

    for (int i = 0; i < num_rows; i++) {
        int result;

        if (strcmp(operation, "and") == 0) {
            result = 1;
            for (int j = 0; j < num_vars; j++) {
                result &= truth_table[i][j];
            }
        } else if (strcmp(operation, "nand") == 0) {
            result = 1;
            for (int j = 0; j < num_vars; j++) {
                result &= truth_table[i][j];
            }
            result = !result;
        } else if (strcmp(operation, "or") == 0) {
            result = 0;
            for (int j = 0; j < num_vars; j++) {
                result |= truth_table[i][j];
            }
        } else if (strcmp(operation, "nor") == 0) {
            result = 0;
            for (int j = 0; j < num_vars; j++) {
                result |= truth_table[i][j];
            }
            result = !result;
        } else if (strcmp(operation, "xor") == 0) {
            result = 0;
            for (int j = 0; j < num_vars; j++) {
                result ^= truth_table[i][j];
            }
        } else if (strcmp(operation, "buf") == 0) {
            result = truth_table[i][0]; // Buffer gate simply outputs the first input value
        } else if (strcmp(operation, "not") == 0) {
            if (num_vars != 1) {
                printf("NOT operation requires exactly one input variable\n");
                free(results);
                return NULL;
            }
            result = !truth_table[i][0]; // NOT gate inverts the first input value
        } else {
            printf("Unsupported operation: %s\n", operation);
            free(results); // Free the allocated memory for results if operation is unsupported
            return NULL;
        }

        results[i] = result; // Store the result in the results array
    }

    return results; // Return the results array
}


int main_2() {
    int num_vars = 2;
    int num_rows;
    int** truth_table = generate_truth_table(num_vars, &num_rows);

           // Print truth table
                    std::cout << "Truth Table:" << std::endl;
                    for (int i = 0; i < num_rows; ++i) {
                        for (int j = 0; j < num_vars; ++j) {
                            std::cout << truth_table[i][j] << " ";
                        }
                        std::cout << std::endl;
                    }

   // Example: Process the truth table with the AND operation
    int* results = process_truth_table(truth_table, num_rows, num_vars, "or");

    // Print the results
    printf("Results for operation 'and': {");
    for (int i = 0; i < num_rows; i++) {
        printf("%d", results[i]);
        if (i < num_rows - 1) {
            printf(", ");
        }
    }
    printf("}\n");


    // Free allocated memory
    for (int i = 0; i < num_rows; i++) {
        free(truth_table[i]);
    }
    free(truth_table);

    return 0;
}

std::vector<double> processResultsToProbabilities(int* results, int num_rows) {
    std::vector<double> probabilities;
    probabilities.reserve(2 * num_rows); // Reserve space for efficiency

    for (int i = 0; i < num_rows; ++i) {
        int inverted_value = (results[i] == 1) ? 0 : 1;
        probabilities.push_back(inverted_value);
        probabilities.push_back(results[i]);
    }

    return probabilities;
}

void freeProbabilities(std::vector<double>& probabilities) {
    // Clear the vector and release the memory
    probabilities.clear();
    probabilities.shrink_to_fit();
}


int main()
{
    // "/home/lemy/project01.v"
    // "/home/lemy//Desktop/ISCAS./Verilog3/C880.v"
    std::string filePath = "C880.v"; // **************************************************************************************************************
    printf("Starting Circuit Network..\n");
    sleep(5);
    std::vector<std::vector<std::string>> nodes = read_verilog(filePath);
    std::vector<std::string> inputs = get_inputs(filePath);
    
    
    
    // show errors and warnings in the console
    DSL_errorH().RedirectToFile(stdout);

    DSL_network net;

     // Print the size of nodes (number of inner vectors)
    std::cout << "Size of nodes: " << nodes.size() << std::endl;
    std::cout << "\nSize of inputs: " << inputs.size() << std::endl;
    sleep(5);
    std::map<std::string, int> dynamicVariables;
    std::cout << "\nCreating nodes to net ..." << std::endl;
     for (const auto& vec : nodes) {
        int k = 0;
        int pass = 10;
        std::string logic;
        for (const auto& str : vec) {
             if(k == 0){
                logic = str;
                // std::cout << "." << logic << "."  << std::endl;
            }
            if(k == 1){
              int e = CreateCptNode(net, str.c_str(),  logic.c_str(), 
                                    { "0", "1"}, 60, 40); 
              
               dynamicVariables[str.c_str()] = e;  
            }
            k++;}}
    
     std::cout << "\nDone!" << std::endl;
     sleep(5);
     std::cout << "\nCreating arcs to net ..." << std::endl;
     for (const auto& vec : nodes) {
        int k = 0;
        for (const auto& str : vec) {
            if(k == 1){
              // we are in the current node here
              std::vector<std::string> children = get_children_from_node(str.c_str(),nodes);
              
              for (const auto& child : children) {
        
                    net.AddArc(dynamicVariables[str.c_str()], dynamicVariables[child]);
                                                }
                          

            }
            k++;}}
    std::cout << "\nDone!" << std::endl;
    // create inputs nodes to net
    sleep(5);        
    std::cout << "\nCreating inputs nodes to net ..." << std::endl;
    for (const auto& str : inputs) {
              std::cout << "input is being add to nodes  " << str.c_str() << std::endl;
              int e = CreateCptNode(net, str.c_str(), "input", { "0", "1"}, 60, 40); 
              dynamicVariables[str.c_str()] = e;  
           }
    std::cout << "\nDone!" << std::endl; 
    sleep(3);
    std::cout << "\nCreating arcs to inputs nodes ..." << std::endl;

    for (const auto& str : inputs) {
              std::vector<std::string> children = get_children_from_node(str.c_str(),nodes);
              
              for (const auto& child : children) {
                    //std::cout << "child of: " << str << " is " << child << std::endl;
                    net.AddArc(dynamicVariables[str.c_str()], dynamicVariables[child]);
                                                }
           }      
    
    sleep(3);
    std::cout << "\nSetting Probability to inputs nodes ..." << std::endl;
     for (const auto& str : inputs) {

            int res = net.GetNode(dynamicVariables[str.c_str()])->Def()->SetDefinition({
            0.5, // P(node = 0)
            0.5 // P(node = 1)
               });
                    if (DSL_OKAY != res)
                    {
                        return res;
                    }
              
           }     

    sleep(5);
     std::cout << "\nSetting Probability to internal nodes ..." << std::endl;
     for (const auto& vec : nodes) {
        std::string logic;
        int k = 0;
        for (const auto& str : vec) {
            if(k == 0){
                logic = str;
                // std::cout << "." << logic << "."  << std::endl;
            }
            if(k == 1){
                std::cout << "Node: " << str.c_str() << std::endl;
                // set prob here
                int num_vars = vec.size() - 2;
                int num_rows;
                int** truth_table = generate_truth_table(num_vars, &num_rows);

                        // Print truth table
                    std::cout << "Truth Table:" << std::endl;
                    for (int i = 0; i < num_rows; ++i) {
                        for (int j = 0; j < num_vars; ++j) {
                            std::cout << truth_table[i][j] << " ";
                        }
                        std::cout << std::endl;
                    }
                    
                int* results = process_truth_table(truth_table, num_rows, num_vars, logic.c_str());
                

                        // Print results
                    std::cout << "Vector of proba:" << std::endl;
                    for (int i = 0; i < num_rows; ++i) {
                        std::cout << results[i] << " ";
                    }
                    std::cout << std::endl;
                 // Process results to probabilities
                std::vector<double> probabilities = processResultsToProbabilities(results, num_rows);

                // Free the allocated space
                
                int res = net.GetNode(dynamicVariables[str.c_str()])->Def()->SetDefinition(probabilities);
                freeProbabilities(probabilities);

            /*  std::cout << "num_rows:"<< num_rows << std::endl;
                std::vector<double> probabilities;
                for (int i = 0; i < num_rows; ++i) {
                    probabilities.push_back(results[i] / 1.0); // Assuming integers represent probabilities in tenths (e.g., 2 represents 0.2)
                    probabilities.push_back(0);
                }  */ 

                if (DSL_OKAY != res)
                    {
                        
                        std::cout << " node with error" << std::endl;
                    }
                //std::cout << "probabilities: " << probabilities[0] << std::endl;

                // Free allocated memory
                for (int i = 0; i < num_rows; i++) {
                    free(truth_table[i]);
                }
                free(truth_table);
                free(results);
               
                          

            }
            k++;}}
    // Iterate over the map using a range-based for loop
    //    for (const auto& pair : dynamicVariables) {
    //        std::cout << "Key: " << pair.first << ", Value: " << pair.second << std::endl;
    //    }
    //std::cout << "Value corresponding to key " << "w1" << " is " << dynamicVariables["w1"] << std::endl;

    //net.AddArc(dynamicVariables["w1"], dynamicVariables["cout"]);
    //net.AddArc(dynamicVariables["w2"], dynamicVariables["cout"]);

    // std::vector<std::string> children = get_children_from_node("t_66",nodes);
 
       

/*
   int e = CreateCptNode(net, "Economy", "State of the economy", 
        { "Up", "Flat", "Down" }, 160, 40);

    int s = CreateCptNode(net, "Success", "Success of the venture", 
        { "Success", "Failure" }, 60, 40);
    
    int f = CreateCptNode(net, "Forecast", "Expert forecast", 
        { "Good", "Moderate", "Poor" }, 110, 140);

    net.AddArc(e, s);
    net.AddArc(s, f);
    net.AddArc(e, f);

    int res = net.GetNode(e)->Def()->SetDefinition({
        0.2, // P(Economy=U)
        0.7, // P(Economy=F)
        0.1  // P(Economy=D)
    });
    if (DSL_OKAY != res)
    {
        return res;
    }

    res = net.GetNode(s)->Def()->SetDefinition({
        0.3, // P(Success=S|Economy=U)
        0.7, // P(Success=F|Economy=U)
        0.2, // P(Success=S|Economy=F)
        0.8, // P(Success=F|Economy=F)
        0.1, // P(Success=S|Economy=D)
        0.9  // P(Success=F|Economy=D)
    });
    if (DSL_OKAY != res)
    {
        return res;
    }

    res = net.GetNode(f)->Def()->SetDefinition({
        0.70, // P(Forecast=G|Success=S,Economy=U)
        0.29, // P(Forecast=M|Success=S,Economy=U)
        0.01, // P(Forecast=P|Success=S,Economy=U)
        0.65, // P(Forecast=G|Success=S,Economy=F)
        0.30, // P(Forecast=M|Success=S,Economy=F)
        0.05, // P(Forecast=P|Success=S,Economy=F)
        0.60, // P(Forecast=G|Success=S,Economy=D)
        0.30, // P(Forecast=M|Success=S,Economy=D)
        0.10, // P(Forecast=P|Success=S,Economy=D)
        0.15, // P(Forecast=G|Success=F,Economy=U)
        0.30, // P(Forecast=M|Success=F,Economy=U)
        0.55, // P(Forecast=P|Success=F,Economy=U)
        0.10, // P(Forecast=G|Success=F,Economy=F)
        0.30, // P(Forecast=M|Success=F,Economy=F)
        0.60, // P(Forecast=P|Success=F,Economy=F)
        0.05, // P(Forecast=G|Success=F,Economy=D)
        0.25, // P(Forecast=G|Success=F,Economy=D)
        0.70  // P(Forecast=G|Success=F,Economy=D)
    }); 
    if (DSL_OKAY != res)
    {
        return res;
    }  */

    int res = net.WriteFile("C880_v.xdsl");
    if (DSL_OKAY != res)
    {
        return res;
    } 

    printf("\nNetwork has been written to bn_from_circuit.xdsl\n");
    return DSL_OKAY;   
    return 0;
}


static int CreateCptNode(
	DSL_network &net, const char *id, const char *name, 
    std::initializer_list<const char *> outcomes, int xPos, int yPos)
{
    int handle = net.AddNode(DSL_CPT, id);
    DSL_node *node = net.GetNode(handle);
    node->SetName(name);
    node->Def()->SetNumberOfOutcomes(outcomes);
    DSL_rectangle &position = node->Info().Screen().position;
    position.center_X = xPos;
    position.center_Y = yPos;
    position.width = 85;
    position.height = 55;
    return handle;
}

