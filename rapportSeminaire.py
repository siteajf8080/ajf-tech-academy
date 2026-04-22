import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Preparasyon done yo baze sou tablo ou a
data = {
    'Ane': [2023, 2023, 2023, 2023, 2024, 2024, 2024, 2024, 2024, 2025, 2025, 2026, 2026],
    'Lokalite': ['Port-Salut', 'Les Cayes', 'Torbeck', 'Les Cayes', 
                 'Torbeck', 'Les Cayes', 'Chantal', 'Camp-Perrin', 'BTI (Cayes)', 
                 'BTI (Cayes)', 'Les Cayes', 'Session Spéciale', 'Les Cayes'],
    'Participants': [14, 5, 12, 13, 21, 14, 33, 17, 60, 65, 53, 82, 17]
}

df = pd.DataFrame(data)

# Nou gwoupe done yo pa Ane ak Lokalite pou nou gen total la
df_grouped = df.groupby(['Ane', 'Lokalite'])['Participants'].sum().reset_index()

# Konfigirasyon style graf la
plt.figure(figsize=(14, 8))
sns.set_style("whitegrid")

# Kreye yon graf "Stacked Bar" pou montre evolisyon an
plot = sns.barplot(data=df_grouped, x='Ane', y='Participants', hue='Lokalite', palette='viridis')

# Ajoute tit ak etikèt pwofesyonèl
plt.title('Evolisyon ak Repartisyon Geografik Benefisye AJF-Tech (2023-2026)', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Ane Fiskal', fontsize=12)
plt.ylabel('Kantite Jèn ki Fòme', fontsize=12)
plt.legend(title='Lokalite / Sant', bbox_to_anchor=(1.05, 1), loc='upper left')

# Ajoute chif yo anlè chak seksyon bar
for p in plot.patches:
    if p.get_height() > 0:
        plot.annotate(format(p.get_height(), '.0f'), 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha = 'center', va = 'center', 
                       xytext = (0, 9), 
                       textcoords = 'offset points',
                       fontsize=10, fontweight='bold')

plt.tight_layout()
plt.show()