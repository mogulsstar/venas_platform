import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Box,
  Container,
  Grid,
  Typography,
  Paper,
  Card,
  CardContent,
  CardActionArea,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  TextField,
  InputAdornment,
  CircularProgress,
  Chip,
  Button,
  Tabs,
  Tab,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ArticleIcon from '@mui/icons-material/Article';
import HelpIcon from '@mui/icons-material/Help';
import CategoryIcon from '@mui/icons-material/Category';
import BookmarkIcon from '@mui/icons-material/Bookmark';

import { AppDispatch, RootState } from '../../store';
import { fetchHelpArticles, fetchHelpCategories } from '../../features/help/helpSlice';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`help-tabpanel-${index}`}
      aria-labelledby={`help-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const HelpCenterPage: React.FC = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { articles, categories, loading } = useSelector((state: RootState) => state.help);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    console.log('HelpCenterPage - Fetching help articles and categories');
    dispatch(fetchHelpArticles())
      .unwrap()
      .then(articles => {
        console.log('Help articles fetched successfully:', articles);
      })
      .catch(error => {
        console.error('Failed to fetch help articles:', error);
      });

    dispatch(fetchHelpCategories())
      .unwrap()
      .then(categories => {
        console.log('Help categories fetched successfully:', categories);
      })
      .catch(error => {
        console.error('Failed to fetch help categories:', error);
      });
  }, [dispatch]);

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const handleCategoryClick = (category: string) => {
    setSelectedCategory(category === selectedCategory ? null : category);
  };

  const handleArticleClick = (id: number) => {
    navigate(`/help/articles/${id}`);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Filter articles based on search term and selected category
  const filteredArticles = Array.isArray(articles) ? articles.filter((article) => {
    const matchesSearch =
      searchTerm === '' ||
      article.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      article.content.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesCategory = selectedCategory === null || article.category === selectedCategory;

    return matchesSearch && matchesCategory;
  }) : [];

  // Group articles by category
  const articlesByCategory = Array.isArray(categories) ? categories.reduce((acc, category) => {
    acc[category] = filteredArticles.filter(article => article.category === category);
    return acc;
  }, {} as Record<string, typeof filteredArticles>) : {};

  if (loading && (!Array.isArray(articles) || articles.length === 0)) {
    return (
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {t('help.title')}
        </Typography>

        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            {t('help.howCanWeHelp')}
          </Typography>

          <TextField
            fullWidth
            placeholder={t('help.searchPlaceholder')}
            variant="outlined"
            value={searchTerm}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 3 }}
          />

          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {Array.isArray(categories) && categories.map((category) => (
              <Chip
                key={category}
                label={t(`help.categories.${category.toLowerCase()}`, { defaultValue: category })}
                onClick={() => handleCategoryClick(category)}
                color={selectedCategory === category ? 'primary' : 'default'}
                icon={<CategoryIcon />}
              />
            ))}
          </Box>
        </Paper>

        <Box sx={{ width: '100%' }}>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={handleTabChange} aria-label="help tabs">
              <Tab label={t('help.allArticles')} />
              <Tab label={t('help.byCategory')} />
            </Tabs>
          </Box>

          <TabPanel value={tabValue} index={0}>
            <Grid container spacing={3}>
              {filteredArticles.length > 0 ? (
                filteredArticles.map((article) => (
                  <Grid item xs={12} md={6} lg={4} key={article.id}>
                    <Card>
                      <CardActionArea onClick={() => handleArticleClick(article.id)}>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                            <ArticleIcon sx={{ mr: 2, color: 'primary.main' }} />
                            <Box>
                              <Typography variant="h6" component="div">
                                {article.title}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                                {article.content.substring(0, 100)}...
                              </Typography>
                              <Box sx={{ display: 'flex', mt: 2, gap: 1 }}>
                                <Chip
                                  label={t(`help.categories.${article.category.toLowerCase()}`, { defaultValue: article.category })}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                                {article.tags.map((tag) => (
                                  <Chip
                                    key={tag}
                                    label={tag}
                                    size="small"
                                    variant="outlined"
                                  />
                                ))}
                              </Box>
                            </Box>
                          </Box>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                ))
              ) : (
                <Grid item xs={12}>
                  <Paper sx={{ p: 3, textAlign: 'center' }}>
                    <Typography variant="h6">
                      {t('help.noArticlesFound')}
                    </Typography>
                    <Button
                      variant="outlined"
                      sx={{ mt: 2 }}
                      onClick={() => {
                        setSearchTerm('');
                        setSelectedCategory(null);
                      }}
                    >
                      {t('help.clearFilters')}
                    </Button>
                  </Paper>
                </Grid>
              )}
            </Grid>
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            {Array.isArray(categories) && categories.map((category) => (
              <Box key={category} sx={{ mb: 4 }}>
                <Typography variant="h5" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                  <CategoryIcon sx={{ mr: 1 }} />
                  {t(`help.categories.${category.toLowerCase()}`, { defaultValue: category })}
                </Typography>

                {articlesByCategory[category] && articlesByCategory[category].length > 0 ? (
                  <List component={Paper}>
                    {articlesByCategory[category].map((article, index) => (
                      <React.Fragment key={article.id}>
                        <ListItem button onClick={() => handleArticleClick(article.id)}>
                          <ListItemIcon>
                            <ArticleIcon />
                          </ListItemIcon>
                          <ListItemText
                            primary={article.title}
                            secondary={article.content.substring(0, 100) + '...'}
                          />
                        </ListItem>
                        {index < articlesByCategory[category].length - 1 && <Divider />}
                      </React.Fragment>
                    ))}
                  </List>
                ) : (
                  <Paper sx={{ p: 2 }}>
                    <Typography variant="body1" color="text.secondary">
                      {t('help.noCategoryArticles')}
                    </Typography>
                  </Paper>
                )}
              </Box>
            ))}
          </TabPanel>
        </Box>
      </Box>
    </Container>
  );
};

export default HelpCenterPage;
