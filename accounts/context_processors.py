def company_context(request):
    company = getattr(request, "company", None)
    return {"current_company": company}
