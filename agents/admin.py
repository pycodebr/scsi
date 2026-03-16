from django.contrib import admin

from agents.models import Agent, Producer


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent_type', 'cpf_cnpj', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['agent_type', 'is_active', 'state']
    search_fields = ['name', 'cpf_cnpj', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'cpf', 'agent', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'agent']
    search_fields = ['name', 'cpf', 'email']
    readonly_fields = ['created_at', 'updated_at']
