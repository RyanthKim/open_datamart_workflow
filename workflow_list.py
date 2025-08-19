# 리대시 쿼리 번호
redash_query_number_list = [
        # main
        3155, #custom_plan_info
        1319, #custom_test_plan_list
        1284, #custom_test_account_list
        1272, #custom_docu_creation
        3044, #custom_plan_subscription_periods / custom_plan_subscription_usage_reset_periods / custom_plan_subscription_payment_renew_periods / custom_plan_subscription_monthly_periods
        5197, #custom_active_admin_user_info
        5189, #custom_archived_user
        
        # snapshot
        2973, #temp_week_active_owner_week_log_update
        2972, #temp_week_active_owner_month_log_update
        
        # ddb
        3096, #custom_field_usage_all
        5392, #custom_field_rawdata
        1673, #custom_participant_all_data(requester + signer)
        1353, #custom_participant_data
        
        # monthly indicators
        3721, #custom_workspace_admin_log
        5356, #custom_daily_user_counts
        5403, #custom_daily_total_user_counts
        5394, #custom_daily_signature_counts
        5395, #custom_daily_enterprise_counts
        5354, #custom_daily_document_counts
        5397, #custom_daily_paid_user_counts
        5426, #csstom_daily_signer_counts
        
        # dependent
        4800, #custom_participant_signin_info  의존성 : custom_participant_data, custom_docu_creation
        5304 #custom_payment_billing_rawdata 의존성 : custom_custom_invoice_category, custom_custom_invoice_category_value
    ]

# sheet_id : 시트ID , 
# sheet_name : 시트탭 이름, 
# table_name : 업데이트할 redshift 테이블명
sheet_update_list = [ 
        {"sheet_id":"SHEET_ID", "sheet_name":"categoryRaw", "table_name":"custom_custom_invoice_category"},
        {"sheet_id":"SHEET_ID", "sheet_name":"categoryInfo", "table_name":"custom_custom_invoice_category_value"}
    ]


# create table custom_document_category (
#                 documentid varchar(65535) PRIMARY KEY,
#                 userid varchar(65535),
#                 workspaceid varchar(65535),
#                 estimated_workspaceid varchar(65535),
#                 createdat DATETIME,
#                 nouns varchar(65535),
#                 category1 varchar(65535),
#                 category2 varchar(65535));
# 문서 카테고리 형태소 분석 메서드 필수값
document_title_mining_value = {
    "sql":'''
        select
            d.id as documentid,
            d.userid,
            d.workspaceid,
            d_origin.title,
            d.estimated_workspaceid,
            d.createdat
        from demo_docu_creation d
        left join demo_document d_origin on d_origin.id = d.id
        left join demo_test_user tu on tu.userid = d.userid
        where tu.userid is null
        and d.id not in (select documentid from demo_document_category)
    ''',
    "table_name":'custom_document_category',
    "column_names":['documentid', 'userid', 'workspaceid', 'estimated_workspaceid', 'createdat', 'nouns', 'category1', 'category2'],
    "process_type":'document',
    "delete_table":False,
    "json_file_path_category1":'./resource/documentCategoryJson/dicCategory1.json',
    "json_file_path_category2":'./resource/documentCategoryJson/dicCategory2.json',
    "dic_file_path":'./resource/documentCategoryJson/dic_user.txt'
}


# create table custom_template_category (
#                 templateid varchar(65535) PRIMARY KEY,
#                 workspaceid varchar(65535),
#                 memberid varchar(65535),
#                 title varchar(65535),
#                 createdat DATETIME,
#                 nouns varchar(65535),
#                 category1 varchar(65535),
#                 category2 varchar(65535));
# 템플릿 카테고리 형태소 분석 메서드 필수값
template_title_mining_value = {
    "sql":'''
        WITH TEST_WORKSPACE AS
        (SELECT DISTINCT m.workspaceid
        FROM demo_test_user tu
        JOIN demo_member m ON m.userid = tu.userid)

        SELECT t.id as templateid,
            t.workspaceid,
            t.memberid,
            t.title,
            t.createdat
        FROM demo_template t
        WHERE t.workspaceid NOT IN
            (SELECT workspaceid
            FROM TEST_WORKSPACE)
        and t.id not in (select templateid from demo_template_category)
    ''',
    "table_name":'custom_template_category',
    "column_names":['templateid', 'workspaceid', 'memberid', 'title', 'createdat', 'nouns', 'category1', 'category2'],
    "process_type":'template',
    "delete_table":True,
    "json_file_path_category1":'./resource/documentCategoryJson/dicCategory1.json',
    "json_file_path_category2":'./resource/documentCategoryJson/dicCategory2.json',
    "dic_file_path":'./resource/documentCategoryJson/dic_user.txt'
}


# create table custom_document_form_category (
#                 documentid varchar(65535) PRIMARY KEY,
#                 userid varchar(65535),
#                 workspaceid varchar(65535),
#                 estimated_workspaceid varchar(65535),
#                 createdat DATETIME,
#                 nouns varchar(65535),
#                 category1 varchar(65535));
# 서식 카테고리 형태소 분석 메서드 필수값
document_title_to_form_mining_value = {
    "sql":'''
        select
            d.id as documentid,
            d.userid,
            d.workspaceid,
            d_origin.title,
            d.estimated_workspaceid,
            d.createdat
        from demo_docu_creation d
        left join demo_document d_origin on d_origin.id = d.id
        left join demo_test_user tu on tu.userid = d.userid
        where tu.userid is null
        and d.id not in (select documentid from demo_document_form_category)
    ''',
    "table_name":'custom_document_form_category',
    "column_names":['documentid', 'userid', 'workspaceid', 'estimated_workspaceid', 'createdat', 'nouns', 'category1'],
    "process_type":'document',
    "delete_table":False,
    "json_file_path":'./resource/formCategoryJson/formCategory1.json',
    "dic_file_path":'./resource/formCategoryJson/dic_user.txt'
}


# CREATE TABLE custom_template_form_category (
#     templateid VARCHAR(65535) PRIMARY KEY, 
#     workspaceid VARCHAR(65535),
#     memberid VARCHAR(65535),
#     title VARCHAR(65535), 
#     createdat TIMESTAMP,
#     nouns VARCHAR(65535),
#     category1 VARCHAR(65535)
# );
template_title_to_form_mining_value = {
    "sql":'''
        WITH TEST_WORKSPACE AS
        (SELECT DISTINCT m.workspaceid
        FROM demo_test_user tu
        JOIN demo_member m ON m.userid = tu.userid)

        SELECT t.id as templateid,
            t.workspaceid,
            t.memberid,
            t.title,
            t.createdat
        FROM demo_template t
        WHERE t.workspaceid NOT IN
            (SELECT workspaceid
            FROM TEST_WORKSPACE)
        and t.id not in (select templateid from demo_template_form_category)
    ''',
    "table_name":'custom_template_form_category',
    "column_names":['templateid', 'workspaceid', 'memberid', 'title', 'createdat', 'nouns', 'category1'],
    "process_type":'template',
    "delete_table":True,
    "json_file_path":'./resource/formCategoryJson/formCategory1.json',
    "dic_file_path":'./resource/formCategoryJson/dic_user.txt'
}
