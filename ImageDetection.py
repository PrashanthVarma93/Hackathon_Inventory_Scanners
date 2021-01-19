#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 15:58:10 2021

@author: p0b02sd
"""

from imageai.Detection import ObjectDetection
import os
import sys
import pandas as pd 
import mpld3

#execution_path = os.getcwd()
#execution_path , "resnet50_coco_best_v2.1.0.h5"))

def image_detection(model_path,image_input_path,image_output_path):
    detector = ObjectDetection()
    detector.setModelTypeAsRetinaNet()
    detector.setModelPath( model_path)
    detector.loadModel()
    detections = detector.detectObjectsFromImage(input_image=os.path.join(image_input_path), output_image_path=os.path.join(image_output_path))
    return detections
  

def find_max_prob_obj(detections):
    max_prob_obj=0
    for eachObject in detections:
        print(eachObject["name"] , " : " , eachObject["percentage_probability"] )
        if (eachObject["percentage_probability"] > max_prob_obj): 
            obj_name=eachObject["name"] 
            max_prob_obj=eachObject["percentage_probability"]
    print("\n"+"object detected : " + obj_name)       
    return obj_name      
  
def get_mds_fam_id(item_mds_fam_id_lkp_path,obj_name):
    mds_fam_df=pd.read_csv(item_mds_fam_id_lkp_path)
    mds_fam_id=mds_fam_df[mds_fam_df['item_name']==obj_name]["mds_fam_id"].values[0]
    return mds_fam_id

def get_mds_fam_reatil_df(retail_inventory_data_path,mds_fam_id):
    reatil_inventory_df=pd.read_csv(retail_inventory_data_path)
    mds_fam_reatil_df=reatil_inventory_df[reatil_inventory_df['mds_fam_id']==mds_fam_id]
    return mds_fam_reatil_df
def generate_plot(mds_fam_reatil_df,mds_fam_id,final_plot_path):
    df2 = mds_fam_reatil_df[["item_desc_1","totl_onhands","totl_on_order","totl_inwhse","totl_intransit"]]
    ax2 = df2.plot.bar(x='item_desc_1',color=['#10807d','#ffff14','#e8e8b5','#a1efce'], rot=0)
    ax2.set_xlabel(mds_fam_reatil_df['item_desc_1'].values[0])
    ax2.set_ylabel("No of items")
    fig2 = ax2.get_figure()
    df3=mds_fam_reatil_df[["item_desc_1","forecasted_4wk_ord_qty","demand_4wk"]]
    ax3 = df3.plot.bar(x='item_desc_1', color=['#145fa4','#040701'], rot=0)
    ax3.set_xlabel(mds_fam_reatil_df['item_desc_1'].values[0])
    ax3.set_ylabel("No of items")
    fig3 = ax3.get_figure()
    df4 = mds_fam_reatil_df[["item_desc_1","totl_repl_store","totl_store_outs"]]
    ax4 = df4.plot.bar(x='item_desc_1', color=['#454ae8','#e32227'], rot=0)
    ax4.set_xlabel(mds_fam_reatil_df['item_desc_1'].values[0])
    ax4.set_ylabel("No of items")
    fig4 = ax4.get_figure()
    mds_fam_reatil_df['out_of_stk_percent'] = 100 - mds_fam_reatil_df['in_stk_percent']
    df5 = mds_fam_reatil_df[["in_stk_percent","out_of_stk_percent"]]
    df6 = pd.DataFrame({'Stock Status': df5.values.tolist()[0]}, index=['In Stock', 'Out of Stock'])
    ax5 = df6.plot.pie(y='Stock Status', colors = ['#ff4d4d','#828282'], autopct='%1.1f%%', startangle=90, figsize=(5, 5))
    fig5 = ax5.get_figure()
    f = open(final_plot_path, "w")
    f.write("<HTML><HEAD><TITLE>Inventory Details</TITLE>")
    f.write("<style> h3 {text-align: center;}</style>")
    f.write("</head>")
    f.write("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    f.write("<link rel=\"stylesheet\" href=\"https://www.w3schools.com/w3css/4/w3.css\">")
    f.write("<BODY>")
    f.write("<div class=\"w3-container\">")
    f.write("<h3>Item Inventory Status</h3>")
    i = int(mds_fam_reatil_df["totl_onhands"].values[0]/mds_fam_reatil_df["forecasted_4wk_ord_qty"].values[0]*100)
    if (i >= 100):
        f.write("<div class=\"w3-dark-gray w3-hover-gray\"><div class=\"w3-teal\" style=\"height:38px;width:100%\"><button class=\"w3-button w3-block\">In full (100%)</button></div></div>")
    elif (i >= 75 and i< 100):
        f.write("<div class=\"w3-dark-gray w3-hover-gray\"><div class=\"w3-teal\" style=\"height:38px;width:"+str(i)+"%\"><button class=\"w3-button w3-block\">~ In full ("+str(i)+"%)</button></div></div>")
    elif (i >= 40 and i < 75):
        f.write("<div class=\"w3-dark-gray w3-hover-gray\"><div class=\"w3-blue\" style=\"height:38px;width:"+str(i)+"%\"><button class=\"w3-button w3-block\">~ Half filled ("+str(i)+"%)</button></div></div>")
    elif (i>=15 and i < 40):
        f.write("<div class=\"w3-dark-gray w3-hover-gray\"><div class=\"w3-red\" style=\"height:38px;width:"+str(i)+"%\"><button class=\"w3-button w3-block\">~ Out of Stock ("+str(i)+"%)</button></div></div>")
    elif (i < 15):
        f.write("<div class=\"w3-dark-gray w3-hover-gray\"><div class=\"w3-red\" style=\"height:38px;width:15%\"><button class=\"w3-button w3-block\">~ Out of Stock ("+str(i)+"%)</button></div></div>")
    f.write("</div>")
    f.write("<CENTER>")
    f.write("<br><br>")
    #f.write("<left>")
    f.write("<table>")
    f.write("<tr>")
    f.write("<th><H3>Current Inventory details</H3>&nbsp;&nbsp;</th>")
    f.write("<th><H3>Forecast vs On demand</H3>&nbsp;&nbsp;</th>")
    f.write("</tr>")
    f.write("<tr>")
    f.write("<td>&nbsp;&nbsp;")
    f.write(mpld3.fig_to_html(fig2, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    f.write("</td>")
    #f.write("</left>")
    #f.write("<right>")
    f.write("&nbsp;&nbsp;<td>")
    f.write(mpld3.fig_to_html(fig3, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    f.write("</td>")
    f.write("</tr>")
    #f.write("</right>")
    #f.write("<br>")
    #f.write("<left>")
    f.write("</table>")
    f.write("<table>")
    f.write("<tr>")
    f.write("<th><H3>Store details</H3>&nbsp;&nbsp;</th>")
    f.write("<th><H3>Availability</H3>&nbsp;&nbsp;</th>")
    f.write("</tr>")
    f.write("<tr>")
    f.write("<td>&nbsp;&nbsp;")
    f.write(mpld3.fig_to_html(fig4, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    f.write("</td>")
    #f.write("</left>")
    #f.write("<right>")
    f.write("&nbsp;&nbsp;<td>")
    f.write(mpld3.fig_to_html(fig5, d3_url=None, mpld3_url=None, no_extras=False, template_type='general', figid=None, use_http=False))
    f.write("</td>")
    f.write("</tr>")
    #f.write("</right>")
    #f.write("<br>")
    #f.write("</left>")
    f.write("</table>")
    f.write("</CENTER>")
    f.write("</BODY>")
    f.write("</html>")
    f.close()
        

if __name__ == '__main__':   
   if len(sys.argv) != 7 :
        print("please provide required argumnets")
        exit(1)
   model_path=sys.argv[1]
   image_input_path=sys.argv[2]
   image_output_path=sys.argv[3] 
   item_mds_fam_id_lkp_path=sys.argv[4] 
   retail_inventory_data_path=sys.argv[5] 
   final_plot_path=sys.argv[6] 
   detections=image_detection(model_path,image_input_path,image_output_path)
   obj_name=find_max_prob_obj(detections) 
   mds_fam_id=get_mds_fam_id(item_mds_fam_id_lkp_path,obj_name)
   mds_fam_reatil_df=get_mds_fam_reatil_df(retail_inventory_data_path,mds_fam_id)
   generate_plot(mds_fam_reatil_df,mds_fam_id,final_plot_path)
   

   

       
        
        
        

   
