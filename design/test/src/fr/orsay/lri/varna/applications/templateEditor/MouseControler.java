package fr.orsay.lri.varna.applications.templateEditor;

import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.awt.event.MouseMotionListener;
import java.awt.geom.Point2D;



public class MouseControler implements MouseListener, MouseMotionListener {
	
	private int _granularity = 8;
	private final int HYSTERESIS_DISTANCE = 10;
	TemplatePanel _sp;
	GraphicalTemplateElement _elem;
	TemplateEditorPanelUI _ui;
	
  public MouseControler(TemplatePanel sp, TemplateEditorPanelUI ui)
  {
	  _sp = sp;
	  _elem = null;
	  _ui = ui;
  }

public void mouseClicked(MouseEvent arg0) {
}

public void mouseEntered(MouseEvent arg0) {
	// TODO Auto-generated method stub
	
}

public void mouseExited(MouseEvent arg0) {
	// TODO Auto-generated method stub
	
}

private GraphicalTemplateElement.RelativePosition _currentMode = Helix.RelativePosition.RP_OUTER; 

private Point2D.Double _clickedPos = new Point2D.Double();

public void mousePressed(MouseEvent arg0) {
	GraphicalTemplateElement elem = _sp.getElementAt(arg0.getX(), arg0.getY());
	_clickedPos = new Point2D.Double(arg0.getX(), arg0.getY());
	_sp.Unselect();
	if (elem==null)
	{
		if (arg0.getButton()==MouseEvent.BUTTON1)
		{
			_currentMode = Helix.RelativePosition.RP_EDIT_START;
		}
		else if (arg0.getButton()==MouseEvent.BUTTON3)
		{
			UnpairedRegion n = new UnpairedRegion(arg0.getX(),arg0.getY(),_sp.getTemplate());
			n.setDominantColor(_sp.nextBackgroundColor());
			_ui.addElementUI(n);
			_sp.setSelected(n);
			_sp.repaint();
			_elem = n;
			_currentMode = GraphicalTemplateElement.RelativePosition.RP_EDIT_START;
		}
	}
	else
	{
		_currentMode = elem.getRelativePosition(arg0.getX(), arg0.getY());
		_sp.setSelected(elem);
		_elem = elem;
		switch (_currentMode)
		{
			case RP_EDIT_START:
			case RP_EDIT_END:
			case RP_EDIT_TANGENT_5:
			case RP_EDIT_TANGENT_3:
			break;
			case RP_INNER_MOVE:
				break;
			case RP_INNER_GENERAL:
				_currentMode = Helix.RelativePosition.RP_INNER_MOVE; 
				break;
			case RP_CONNECT_END3:
			case RP_CONNECT_END5:
			case RP_CONNECT_START5:
			case RP_CONNECT_START3:
			{
				Couple<GraphicalTemplateElement,GraphicalTemplateElement.RelativePosition> al = _sp.getPartner(elem, _currentMode);
				boolean isConnected = (al!=null); 
				if (isConnected)
				{
					Connection c = _sp.getConnection(elem, _currentMode);
					_ui.removeConnectionUI(c);
					GraphicalTemplateElement p1 = c._h1;
					GraphicalTemplateElement p2 = c._h2;
					boolean p1IsHelix = (p1 instanceof Helix);
					boolean p1IsUnpaired = (p1 instanceof UnpairedRegion);
					boolean p2IsHelix = (p2 instanceof Helix);
					boolean p2IsUnpaired = (p2 instanceof UnpairedRegion);
					boolean p1StillAttached = (p1 == elem);
					
					if ((p1IsUnpaired && p2IsHelix))
					{
						p1StillAttached = false;
					}
					if (p1StillAttached)
					{ 
						_elem = p2;
						_currentMode = c._edge2;
					}
					else if (!p1StillAttached)
					{ 
						_elem=p1;
						_currentMode = c._edge1;
					}
					
				}
				if (_elem instanceof Helix)
				{ 
					_sp.setPointerPos(new Point2D.Double(arg0.getX(),arg0.getY()));
					_sp.setSelectedEdge(_currentMode);
				}
				_sp.setSelected(_elem);
			}
			break;
			case RP_OUTER:
				_sp.Unselect();
				_elem = null;
		}
		_sp.repaint();
	}
}

public void mouseReleased(MouseEvent arg0) {
	if (_elem!=null)
	{
			switch (_currentMode)
			{
			case RP_EDIT_START:
			case RP_EDIT_END:
			{
				if (_elem instanceof Helix)
				{
					Helix h = (Helix) _elem;
					if (h.getPos().distance(h.getExtent())<10.0)
					{
						_ui.removeElementUI(_elem);
						_sp.Unselect();
					}
				}
			}
				break;
			case RP_INNER_MOVE:
				break;
			case RP_CONNECT_END3:
			case RP_CONNECT_END5:
			case RP_CONNECT_START5:
			case RP_CONNECT_START3:
			{
				GraphicalTemplateElement t = _sp.getElementAt(arg0.getX(), arg0.getY(),_elem);
				if (t!=null)
				{
					GraphicalTemplateElement.RelativePosition edge = t.getClosestEdge(arg0.getX(), arg0.getY());
					_ui.addConnectionUI(_elem,_currentMode,t,edge);
				}
				_sp.setSelectedEdge(Helix.RelativePosition.RP_OUTER);
			}
			break;
		}
		_elem = null;			
	}
	_sp.setSelectedEdge(Helix.RelativePosition.RP_OUTER);
	_currentMode = Helix.RelativePosition.RP_OUTER;
	_sp.repaint();
}


private Point2D.Double projectPoint(int x, int y, Point2D.Double ref)
{
	Point2D.Double result = new Point2D.Double();
	double nx = x-ref.x;
	double ny = y-ref.y;
	double tmp = Double.MIN_VALUE;
	for (int i=0;i<this._granularity;i++)
	{
		double angle = 2.0*Math.PI*((double)i/(double)_granularity);
		double dx = Math.cos(angle);
		double dy = Math.sin(angle);
		double norm  = nx*dx+ny*dy;
		//System.out.println(""+angle+" "+norm);
		if (norm > tmp)
		{
			tmp = norm;
			result.x = ref.x+dx*norm;
			result.y = ref.y+dy*norm;
		}
	}
	return result;
}

public void mouseDragged(MouseEvent arg0) 
{
	if (_elem == null)
	{
		switch (_currentMode)
		{
		case RP_EDIT_START:
		{
			if (_clickedPos.distance(arg0.getX(),arg0.getY())>HYSTERESIS_DISTANCE)
			{
			System.out.println("Creating Helix...");
			Helix h1 = new Helix(arg0.getX(),arg0.getY(),_sp.getTemplate(),_sp.getRNAComponents());
			h1.setDominantColor(_sp.nextBackgroundColor());
			_ui.addElementUI(h1);
			_sp.setSelected(h1);
			_sp.repaint();
			_elem = h1;
			}
		}
		break;
		
		}
	}
	else
	{
		if (_elem instanceof Helix)
		{
			Helix h = (Helix) _elem;
			switch (_currentMode)
			{
			case RP_EDIT_START:
			{
				Point2D.Double d = projectPoint(arg0.getX(),arg0.getY(),h.getPos());
				_ui.setHelixExtentUI(h, d.x,d.y);
			}
			break;
			case RP_EDIT_END:
			{
				Point2D.Double d = projectPoint( arg0.getX(),arg0.getY(),h.getExtent());
				_ui.setHelixPosUI(h, d.x,d.y);
			}
			break;
			case RP_INNER_MOVE:
				_ui.moveHelixUI(h, arg0.getX(),arg0.getY());
				break;
			case RP_CONNECT_END3:
			case RP_CONNECT_END5:
			case RP_CONNECT_START5:
			case RP_CONNECT_START3:
				_sp.setPointerPos(new Point2D.Double(arg0.getX(),arg0.getY()));
				_sp.repaint();				
				break;
			}
		}
		else if (_elem instanceof UnpairedRegion)
		{
			UnpairedRegion ur = (UnpairedRegion) _elem;
			Point2D.Double p = new Point2D.Double(arg0.getX(),arg0.getY());
			switch (_currentMode)
			{
			case RP_EDIT_TANGENT_5:
			{
				_ui.setEdge5TangentUI(ur,arg0.getX(),arg0.getY());
				_sp.repaint();
				break;
			}
			case RP_EDIT_TANGENT_3:
			{
				_ui.setEdge3TangentUI(ur,arg0.getX(),arg0.getY());
				_sp.repaint();
				break;
			}
			case RP_CONNECT_START5:
				_ui.setEdge5UI(ur,arg0.getX(),arg0.getY());
				break;
			case RP_CONNECT_END3:
				_ui.setEdge3UI(ur,arg0.getX(),arg0.getY());
				break;
			}
			_sp.repaint();				
		}
	}
}

public void mouseMoved(MouseEvent arg0) {
	// TODO Auto-generated method stub
	
}
}
