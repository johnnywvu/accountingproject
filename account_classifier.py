from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pandas as pd

def train_account_classifier():
    # Original training data (BS vs IS)
    training_data = {
        'Account Name': [
            'Cash', 'Accounts Receivable', 'Equipment', 'Buildings',
            'Accounts Payable', 'Notes Payable', "Owner's Equity", 'Service Income',
            'Sales Revenue', 'Rent Income', 'Interest Income', 'Utilities Expense',
            'Salaries Expense', 'Advertising Expense', 'Office Supplies Expense', 'Insurance Expense',
            'Interest Expense', 'Capital', 'Accumulated Depreciation', 'Equity',
            "Owner's Withdrawing", 'Drawing'
        ],
        'Category': [
            'BS', 'BS', 'BS', 'BS',
            'BS', 'BS', 'BS', 'IS',
            'IS', 'IS', 'IS', 'IS',
            'IS', 'IS', 'IS', 'IS',
            'IS', 'BS', 'BS', 'BS',
            'BS', 'BS'
        ]
    }

    train_df = pd.DataFrame(training_data)
    vectorizer = TfidfVectorizer()
    x = vectorizer.fit_transform(train_df['Account Name'])
    y = train_df['Category']

    classifier = MultinomialNB()
    classifier.fit(x, y)

    return vectorizer, classifier

def train_revenue_expense_classifier():
    # Training data for Revenues and Expenses (for IS accounts only)
    training_data = {
        'Account Name': [
            'Service Income', 'Sales Revenue', 'Rent Income', 'Interest Income',
            'Utilities Expense', 'Salaries Expense', 'Advertising Expense',
            'Office Supplies Expense', 'Insurance Expense', 'Interest Expense'
        ],
        'Category': [
            'Revenue', 'Revenue', 'Revenue', 'Revenue',
            'Expense', 'Expense', 'Expense',
            'Expense', 'Expense', 'Expense'
        ]
    }

    train_df = pd.DataFrame(training_data)

    # Vectorizing the account names
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(train_df['Account Name'])
    y = train_df['Category']

    # Training the Naive Bayes classifier
    classifier = MultinomialNB()
    classifier.fit(X, y)

    return vectorizer, classifier

def categorize_accounts(df):
    # Step 1: Classify into BS and IS
    vectorizer, classifier = train_account_classifier()
    X_new = vectorizer.transform(df['Account Name'])
    predictions = classifier.predict(X_new)

    # Split accounts into IS and BS
    is_accounts_df = df[predictions == 'IS']
    bs_accounts_df = df[predictions == 'BS']

    # Step 2: For IS accounts, further classify into Revenues and Expenses
    vectorizer_revenue_expense, classifier_revenue_expense = train_revenue_expense_classifier()
    X_new_is = vectorizer_revenue_expense.transform(is_accounts_df['Account Name'])
    is_predictions = classifier_revenue_expense.predict(X_new_is)

    # Further split IS accounts into Revenues and Expenses
    revenues_df = is_accounts_df[is_predictions == 'Revenue'].copy()  # Add .copy() to avoid SettingWithCopyWarning
    expenses_df = is_accounts_df[is_predictions == 'Expense'].copy()  # Add .copy() to avoid SettingWithCopyWarning

    # Add confidence scores using .loc to avoid the SettingWithCopyWarning
    probabilities = classifier_revenue_expense.predict_proba(X_new_is)
    confidence_scores = probabilities.max(axis=1)

    revenues_df.loc[:, 'Confidence'] = confidence_scores[is_predictions == 'Revenue']
    expenses_df.loc[:, 'Confidence'] = confidence_scores[is_predictions == 'Expense']

    # Step 3: Return all results
    return bs_accounts_df, revenues_df, expenses_df
