from django.http import JsonResponse, HttpResponse
import json
from .models import User, Expense
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook
from io import BytesIO
from django.utils.timezone import make_naive

@csrf_exempt
def create_user(request):
    """
    Create a new user with email, name, and mobile number.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON input'}, status=400)
        
        # Validate email and mobile number
        if '@gmail.com' not in data.get("email", ""):
            return JsonResponse({'error': 'Invalid email address'}, status=400)
        if len(data.get('mobile_number', '')) != 10:
            return JsonResponse({'error': 'Invalid mobile number'}, status=400)
        
        # Create the user
        user = User.objects.create(
            email=data['email'],
            name=data['name'],
            mobile_number=data['mobile_number'],
            password=data['password']
        )
        return JsonResponse({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'mobile_number': user.mobile_number
        })
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

def login(request, user_id):
    """
    Handle user login with user ID and password. For Authentication
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON input'}, status=400)
        user = User.objects.filter(id=user_id).first()
        if user and data['password'] == user.password:
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'error': 'Incorrect password'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=400)      

def user_details(request, user_id):
    """
    Retrieve and return details of a user by their ID.
    """
    if request.method == "GET":
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse({
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'mobile_number': user.mobile_number
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def add_expenses(request):
    """
    Add expenses with different split methods: EQUAL, EXACT, PERCENTAGE.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        
        # Handle different split methods
        if data['split_method'] == 'PERCENTAGE':
            total_percentage = sum(split['percentage'] for split in data['splits'])
            if total_percentage != 100:
                return JsonResponse({'error': 'Percentages must add up to 100'}, status=400)
        
        if data['split_method'] == 'EQUAL':
            split_amount = data['amount'] / len(data['participants'])
            for user_id in data['participants']:
                Expense.objects.create(
                    Event=data['event'],
                    user_id=user_id,
                    amount=split_amount,
                    split_method=data['split_method']
                )
        
        elif data['split_method'] == 'EXACT':
            for split in data['splits']:
                Expense.objects.create(
                    Event=data['event'],
                    user_id=split['user_id'],
                    amount=split['amount'],
                    split_method=data['split_method']
                )
        
        elif data['split_method'] == 'PERCENTAGE':
            for split in data['splits']:
                amount = data['amount'] * (split['percentage'] / 100)
                Expense.objects.create(
                    Event=data['event'],
                    user_id=split['user_id'],
                    amount=amount,
                    split_method=data['split_method']
                )
        
        return JsonResponse({'message': 'Expenses added successfully'})
    
    return JsonResponse({'error': 'Invalid method'}, status=400)

@csrf_exempt
def user_expenses(request, user_id):
    """
    Retrieve and return expenses of a specific user.
    """
    try:
        user = User.objects.get(id=user_id)
        splits = Expense.objects.filter(user_id=user_id).all()
        
        if not splits:
            return JsonResponse({'error': 'No expenses found for this user'}, status=404)
        
        split_data = [{
            'Name': user.name,
            'Event': split.Event,
            'amount': split.amount,
            'split_method': split.split_method,
            'paid_time': make_naive(split.created_at).strftime('%Y-%m-%d %H:%M:%S')
        } for split in splits]
        
        return JsonResponse(split_data, safe=False)
    
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
def overall_expenses(request):
    """
    Retrieve and return all expenses for all users.
    """
    users = User.objects.all()
    total_expenses = []
    
    for user in users:
        splits = Expense.objects.filter(user_id=user.id).all()
        each_expenses = [{
            'Name': user.name,
            'Event': split.Event,
            'amount': split.amount,
            'split_method': split.split_method,
            'paid_time': make_naive(split.created_at).strftime('%Y-%m-%d %H:%M:%S')
        } for split in splits]
        total_expenses.append(each_expenses)
    
    return JsonResponse(total_expenses, safe=False)

@csrf_exempt
def download_balance_sheet(request, user_id):
    """
    Generate and download an Excel file containing individual expenses for a specific user
    and total expenses for all users.
    """
    if request.method == "GET":
        workbook = Workbook()
        
        # Create sheet for individual user expenses
        ws1 = workbook.active
        ws1.title = 'Individual Expenses'
        ws1.append(['Name', 'Event', 'Amount', 'Split Method', 'Paid Time'])
        
        try:
            user = User.objects.get(id=user_id)
            splits = Expense.objects.filter(user_id=user_id).all()
            
            for split in splits:
                paid_time = make_naive(split.created_at).strftime('%Y-%m-%d %H:%M:%S')
                ws1.append([
                    user.name,
                    split.Event,
                    split.amount,
                    split.split_method,
                    paid_time
                ])
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        
        # Create sheet for total expenses of all users
        ws2 = workbook.create_sheet(title='Total Expenses')
        ws2.append(['Name', 'Event', 'Amount', 'Split Method', 'Paid Time'])
        
        users = User.objects.all()
        for user in users:
            splits = Expense.objects.filter(user_id=user.id).all()
            for split in splits:
                paid_time = make_naive(split.created_at).strftime('%Y-%m-%d %H:%M:%S')
                ws2.append([
                    user.name,
                    split.Event,
                    split.amount,
                    split.split_method,
                    paid_time
                ])
        
        # Save workbook to an in-memory file
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        
        # Create HTTP response with the Excel file
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="balance_sheet.xlsx"'
        
        return response
    
    return JsonResponse({'error': 'Invalid method'}, status=400)
