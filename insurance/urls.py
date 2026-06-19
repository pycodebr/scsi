from django.urls import path

from .views import (
    EndorsementCreateView,
    EndorsementDetailView,
    EndorsementListView,
    EndorsementUpdateView,
    GeneratePolicyFromProposalView,
    PolicyCreateView,
    PolicyDetailView,
    PolicyItemsJsonView,
    PolicyListView,
    PolicyUpdateView,
    ProposalCreateView,
    ProposalDetailView,
    ProposalListView,
    ProposalUpdateView,
    RenewalCreateView,
    RenewalDetailView,
    RenewalListView,
    RenewalUpdateView,
)

app_name = 'insurance'

urlpatterns = [
    path('propostas/', ProposalListView.as_view(), name='proposal_list'),
    path('propostas/create/', ProposalCreateView.as_view(), name='proposal_create'),
    path('propostas/<int:pk>/', ProposalDetailView.as_view(), name='proposal_detail'),
    path('propostas/<int:pk>/edit/', ProposalUpdateView.as_view(), name='proposal_update'),
    path('propostas/<int:pk>/generate-policy/', GeneratePolicyFromProposalView.as_view(), name='proposal_generate_policy'),
    path('apolices/', PolicyListView.as_view(), name='policy_list'),
    path('apolices/create/', PolicyCreateView.as_view(), name='policy_create'),
    path('apolices/<int:pk>/', PolicyDetailView.as_view(), name='policy_detail'),
    path('apolices/<int:pk>/edit/', PolicyUpdateView.as_view(), name='policy_update'),
    path('apolices/<int:pk>/items-json/', PolicyItemsJsonView.as_view(), name='policy_items_json'),
    path('endossos/', EndorsementListView.as_view(), name='endorsement_list'),
    path('endossos/create/', EndorsementCreateView.as_view(), name='endorsement_create'),
    path('endossos/<int:pk>/', EndorsementDetailView.as_view(), name='endorsement_detail'),
    path('endossos/<int:pk>/edit/', EndorsementUpdateView.as_view(), name='endorsement_update'),
    path('renovacoes/', RenewalListView.as_view(), name='renewal_list'),
    path('renovacoes/create/', RenewalCreateView.as_view(), name='renewal_create'),
    path('renovacoes/<int:pk>/', RenewalDetailView.as_view(), name='renewal_detail'),
    path('renovacoes/<int:pk>/edit/', RenewalUpdateView.as_view(), name='renewal_update'),
]