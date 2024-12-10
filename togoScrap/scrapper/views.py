from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.views import LoginView

from scrapper.utilis.cruiseline_scrapper import main
from django.contrib import messages  
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.core.mail import send_mail
from .tasks import send_email_with_excel
class CustomLoginView(LoginView):
    template_name = 'login.html'
    
    
@csrf_exempt
@login_required
def scrapper(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('fileUpload')
        selected_script = request.POST.get('script')
        
        if uploaded_file and selected_script:  # Ensure both inputs are provided
            try:
                if selected_script == "Cruise Line Scraper":
                    file = main(uploaded_file)
                    filename = 'cruisline'
                elif selected_script == "Interline Cruise Line Scraper":
                    file = main(uploaded_file, "script2")
                    filename = 'interline'
                elif selected_script == "Custom Search Cruise Line Scraper":
                    file = main(uploaded_file, "script3")
                    filename = 'custom search'

                # Return the generated Excel file for download
                response = HttpResponse(file, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
                
            except Exception as e:
                # Return an error JSON response in case of an exception
                return JsonResponse({
                    'status': 'error',
                    'message': f"Error executing {selected_script}: {str(e)}"
                }, status=500)
        else:
            # Return a warning JSON response if file or script is missing
            return JsonResponse({
                'status': 'warning',
                'message': "Please select a script and upload a file."
            }, status=400)

    # send_email_with_excel('cruisline', 'script1')
    return render(request, 'index.html')