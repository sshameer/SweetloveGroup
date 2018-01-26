

#Function to identify net synthesis/consumption of metabolites in a given set of
#reactions 
#args: 1) a solved cobra model 2) a list of reactions from which net metabolite s-
#-toichiometry should be calculated
#output: a dictionay file with metabolite ids as key and net soichiometry as value
def netMetaboliteStoich(cobra_model,rxnlist):
  netMet = dict()
  for rxn in rxnlist:
    rxn = cobra_model.reactions.get_by_id(rxn)
    if round(rxn.x,6)==0:
      print rxn.id+" flux is 0."
      netMet = dict()
      break
    for met in rxn.metabolites:
      if netMet.keys().__contains__(met.id):
        netMet[met.id]=netMet[met.id]+((rxn.x/abs(rxn.x))*rxn.metabolites.get(met))
      else:
        netMet[met.id]=((rxn.x/abs(rxn.x))*rxn.metabolites.get(met))
  return netMet


#Function to print out all reactions generating/consuming a metabolite of inter-
#est 
#args: 1) a solved cobra model 2) metabolite ID 3) ID of alternate charged state
#(use "" if none) 4) output file (use "" if no output file is required)
#output: none
def writeMetabSummary(cobra_model, met, Amet, outfile):
  met=cobra_model.metabolites.get_by_id(met)
  if not Amet == "":
    Amet=cobra_model.metabolites.get_by_id(Amet)
  if not outfile=="":
    fout = open(outfile,"w")
    fout.write("rxn ID\treaction\tmetabolite flux\n")
  for rxn in met.reactions:
    sto=rxn.metabolites.get(met)
    if Amet=="":
      sto1=0
    else:
      sto1=rxn.metabolites.get(Amet)
    if outfile=="":
      print  rxn.id+"\t"+rxn.reaction+"\t"+str(rxn.x*(sto+sto1))
    else:
      fout.write(rxn.id+"\t"+rxn.reaction+"\t"+str(rxn.x*(sto+sto1))+"\n")
  if not outfile=="":
    fout.close()
      
      
#Function to calculate night time carbon conversion efficiency in diel model
#args: 1) a solved cobra model 2) day-night accumulation tag (default = "diel-
#-Transfer") 3) reaction ID for night time output (default = phloem_output_tx-
#-2), 4) reaction ID representing CO2 respired
#output: carbon conversion efficiency
def predictCCE(C3_model,accumulation_tag="dielTransfer",output="Phloem_output_tx2",CO2rxn = "CO2_tx2"):
  import re
  
  for met in C3_model.metabolites:
    if not met.formula:
      met.formula=""
  
  Cin = 0
  Cout = 0
  
  for rxn in C3_model.reactions.query(accumulation_tag):
    if round(rxn.x,5)>0:
      for met in rxn.products:
        #print met
        if met.formula.__contains__("C"):
          #print str(Cin)+"---"+met.id
          #print str(rxn.x)+"\t"+str(rxn.metabolites.get(met))+"\t"+str(int(re.split(r"[C,H]",met.formula)[1]))
          Cin = Cin + (rxn.x * rxn.metabolites.get(met) * int(re.split(r"[C,H]",met.formula)[1]))
  
  for rxn in C3_model.reactions.query(accumulation_tag):
    if round(rxn.x,5)<0:
      for met in rxn.reactants:
        if met.formula.__contains__("C"):
          #print str(Cout)+"---"+met.id
          #print str(rxn.x)+"\t"+str(rxn.metabolites.get(met))+"\t"+str(int(re.split(r"[C,H]",met.formula)[1]))
          Cout = Cout + (rxn.x * rxn.metabolites.get(met) * int(re.split(r"[C,H]",met.formula)[1]))
  
  rxn = C3_model.reactions.get_by_id(output)
  for met in rxn.reactants:
    if met.formula.__contains__("C"):
      #print str(Cout)+"---"+met.id
      #print str(rxn.x)+"\t"+str(-1 * rxn.metabolites.get(met))+"\t"+str(int(re.split(r"[C,H]",met.formula)[1]))
      Cout = Cout + (rxn.x * -1 * rxn.metabolites.get(met) * int(re.split(r"[C,H]",met.formula)[1]))
  
  Cout = Cout + (-1*C3_model.reactions.get_by_id(CO2rxn).x)
  
  if(not round(Cin,5) == round(Cout,5)):
    print "Error, Cin = "+str(Cin)+" and Cout = "+str(Cout)
    return 0
  else:
    print "Cin = "+str(Cin)+"\tCO2 ="+str(C3_model.reactions.get_by_id(CO2rxn).x)+"\t"+str(1 + ((C3_model.reactions.get_by_id(CO2rxn).x)/Cin))
    return 1 + ((C3_model.reactions.get_by_id("CO2_tx2").x)/Cin)



####################################################################
#This function generates a tab seperated file that can be used with#
#Cytoscape to visualize metabolic flux                             #
#                                                                  #
#inputs: 1) a cobra model with feasible solution 2) the number of  #
#cells in the model (eg: 2 for diel C3 and 4 for diel C4) 3) the   #
#name of the output file                                           #
#                                                                  #
####################################################################

def generateFluxMap(cobra_model,phases = 2, outfile)
    import cobra
    solution = cobra.flux_analysis.parsimonious.optimize_minimal_flux(cobra_model)
    #solution = cobra.flux_analysis.parsimonious.pfba(cobra_model)          #If the previous line returns error comment it out and uncomment this line instead

    #open output file for writing
    f = open(outfile);

    #use rxnSet to identify reaction that have already been processed
    rxnSet = set()

    mult=set()
    #Looping through all reactions in the model
    for rxn in cobra_model.reactions:
        #Get the ID
        RXN=rxn.id
        #declare a boolean variable multFlag to keep track of whether this reaction is present in multiple models
        multFlag=False

        #check if the reaction has already been processed before and if yes skip this run in the loop
        if(rxnSet.__contains__(RXN)):
            continue
        if rxn.id.__contains__("EX") or rxn.id.__contains__("Transfer"):
            multFlag=False
        #check if the reaction ends with one or two i.e it is present more than once in the model
        elif(["1","2","3","4","5","6","7","8","9"].__contains__(rxn.id[len(rxn.id)-1])):
            #change the id to without the suffix 1-9 and declare it as a reaction which has multiple instances
            RXN = rxn.id[0:len(rxn.id)-1]
            multFlag=True
        elif rxn.id[len(rxn.id)-2:] == "10":
            #change the id to without the suffix 10 and declare it as a reaction which has multiple instances
            RXN = rxn.id[0:len(rxn.id)-2]
            multFlag=True

        #if metabolite has multiple instances
        values = dict()
        status1 = dict()
        status2 = dict()
        if(multFlag):
            tempvalue = list()
            temp1 = list()
            temp2 = list()
            mult.add(RXN)
            #add the reaction we are about to process to the reactions processed list
            for i in range(1,phases+1):
                rxnSet.add(RXN+str(i))
                if(round(float(cobra_model.reactions.get_by_id(RXN+str(i)).x)*10000) == 0):
                    tempvalue.append(0)
                    temp1.append("none")
                    temp2.append("none")
                elif(float(cobra_model.reactions.get_by_id(RXN+str(i)).x)*10000 > 0):
                    tempvalue.append(cobra_model.reactions.get_by_id(RXN+str(i)).x*1000)
                    temp1.append("produced")
                    temp2.append("consumed")
                elif(float(cobra_model.reactions.get_by_id(RXN+str(i)).x)*10000 < 0):
                    tempvalue.append(cobra_model.reactions.get_by_id(RXN+str(i)).x*1000)
                    temp1.append("consumed")
                    temp2.append("produced")
            values[RXN] = tempvalue
            status1[RXN] = temp1
            status2[RXN] = temp2

            #select 1 reaction so that we can identify the reactants and products which can be then used to generate the edge shared_name
            rxn=cobra_model.reactions.get_by_id(RXN+"1")

            for reac in rxn.reactants:
                REAC=reac.id
                if(REAC.__contains__("1")):
                    if(REAC.rindex("1")==len(REAC)-1) or (REAC.rindex("2")==len(REAC)-1):
                        REAC=REAC[0:len(REAC)-1]
                    f.write("R_"+RXN+" (reaction-reactant) M_"+REAC)
                    for i in range(1,phases+1):
                        f.write("\t"+str(values[RXN][i-1])+"\t"+str(status2[RXN][i-1]))
                    f.write("\n")
                if(RXN.__contains__("biomass")):
                    f.write("R_"+RXN+" (reaction-product)) M_"+REAC)
                    for i in range(1,phases+1):
                        f.write("\t"+str(values[RXN][i-1])+"\t"+str(status1[RXN][i-1]))
                    f.write("\n")
            for prod in rxn.products:
                PROD=prod.id
                if(PROD.__contains__("1")):
                    if(PROD.rindex("1")==len(PROD)-1) or (PROD.rindex("2")==len(PROD)-1):
                        PROD=PROD[0:len(PROD)-1]
                f.write("R_"+RXN+" (reaction-product) M_"+PROD)
                for i in range(1,phases+1):
                    f.write("\t"+str(values[RXN][i-1])+"\t"+str(status1[RXN][i-1]))
                f.write("\n")
            if(RXN.__contains__("biomass")):
                f.write("R_"+RXN+" (reaction-reactant) M_"+REAC)
                for i in range(1,phases+1):
                    f.write("\t"+str(values[RXN][i-1])+"\t"+str(status2[RXN][i-1]))
                f.write("\n")
        else:
            #add the reaction we are about to process to the reactions processed list
            rxnSet.add(RXN)
            if(round(float(solution.x_dict.get(rxn.id))*10000) == 0):
                value = 0;
                status1= "none";
                status0= "none";
            elif(solution.x_dict.get(rxn.id)*10000 > 0):
                value = solution.x_dict.get(rxn.id)*1000;
                status1= "produced";
                status0= "consumed";
            elif(solution.x_dict.get(rxn.id)*10000 < 0):
                value = solution.x_dict.get(rxn.id)*1000;
                status1= "consumed";
                status0= "produced";

            for reac in rxn.reactants:
                REAC=reac.id
                if(REAC.__contains__("1")):
                    if(REAC.rindex("1")==len(REAC)-1):# or (met.id.rindex("2")==len(rxn.id)-1):
                        REAC=REAC[0:len(REAC)-1]
                f.write("R_%s (reaction-reactant) M_%s\t%s\t%s\t0\tnone\n" % (RXN,REAC,value,status0));
            for prod in rxn.products:
                PROD=prod.id
                if(PROD.__contains__("1")):
                    if(PROD.rindex("1")==len(PROD)-1):# or (met.id.rindex("2")==len(rxn.id)-1):
                        PROD=PROD[0:len(PROD)-1]
                f.write("R_%s (reaction-product) M_%s\t%s\t%s\t0\tnone\n" % (RXN,PROD,value,status1));

    f.close();




  
